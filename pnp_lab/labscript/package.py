import ast
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from .language import detect_language
from .runtime import parse_source
from .stdlib import BUILTIN_MODULES


PACKAGE_FORMAT = 1


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _collect_sources(main_file):
    root = main_file.parent
    found = {}

    def visit(path):
        path = path.resolve()
        if path.name in found:
            return

        source = path.read_text(encoding="utf-8")
        _, _, tree = parse_source(source, filename=str(path))
        found[path.name] = path

        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)

        for name in sorted(names):
            if name in BUILTIN_MODULES:
                continue
            if not name or "." in name or "/" in name or "\\" in name:
                raise ValueError(f"non-portable module name: {name!r}")

            candidate = root / f"{name}.lab"
            if not candidate.is_file():
                raise ValueError(
                    f"portable build cannot find local module {name!r} next to {main_file.name}"
                )
            visit(candidate)

    visit(main_file)
    return [found[name] for name in sorted(found)]


def build_package(main_file, output_file=None):
    main_file = Path(main_file).resolve()

    if main_file.suffix != ".lab":
        raise ValueError("LabScript source must use .lab extension")

    source = main_file.read_text(encoding="utf-8")
    language, _ = detect_language(source)
    output_file = Path(output_file or main_file.with_suffix(".labpkg")).resolve()
    sources = _collect_sources(main_file)

    manifest = {
        "format": PACKAGE_FORMAT,
        "main": main_file.name,
        "language": language.value,
        "files": {path.name: file_sha256(path) for path in sources},
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        )
        for path in sources:
            archive.write(path, arcname=f"src/{path.name}")

    return output_file, manifest


def _validate_name(name):
    path = Path(name)
    if path.name != name or path.suffix != ".lab" or name in {"", ".", ".."}:
        raise ValueError(f"unsafe package file name: {name!r}")


def verify_package(path):
    path = Path(path)

    with zipfile.ZipFile(path, "r") as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))

        if manifest.get("format") != PACKAGE_FORMAT:
            raise ValueError(
                f"unsupported LabScript package format: {manifest.get('format')}"
            )

        files = manifest.get("files", {})
        main = manifest.get("main")
        if main not in files:
            raise ValueError("package main file is missing from manifest")

        for name, expected in files.items():
            _validate_name(name)
            payload = archive.read(f"src/{name}")
            actual = hashlib.sha256(payload).hexdigest()
            if actual != expected:
                raise ValueError(f"package hash mismatch: {name}")

    return manifest


def run_package(path, runtime):
    path = Path(path)
    manifest = verify_package(path)

    with tempfile.TemporaryDirectory(prefix="labscript-") as temp_dir:
        source_dir = Path(temp_dir) / "src"
        source_dir.mkdir()

        with zipfile.ZipFile(path, "r") as archive:
            for name in manifest["files"]:
                _validate_name(name)
                payload = archive.read(f"src/{name}")
                (source_dir / name).write_bytes(payload)

        runtime.module_paths.insert(0, source_dir)
        try:
            runtime.execute_file(source_dir / manifest["main"])
        finally:
            runtime.module_paths.pop(0)

    return runtime
