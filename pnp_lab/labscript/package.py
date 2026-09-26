import hashlib
import json
import tempfile
import zipfile
from pathlib import Path

from .language import detect_language


PACKAGE_FORMAT = 1


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_package(main_file, output_file=None):
    main_file = Path(main_file).resolve()

    if main_file.suffix != ".lab":
        raise ValueError("LabScript source must use .lab extension")

    source = main_file.read_text(encoding="utf-8")
    language, _ = detect_language(source)
    output_file = Path(output_file or main_file.with_suffix(".labpkg")).resolve()

    # First package format keeps all local .lab modules from the same folder.
    # No hidden dependency download happens during build or run.
    sources = sorted(main_file.parent.glob("*.lab"))
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


def verify_package(path):
    path = Path(path)

    with zipfile.ZipFile(path, "r") as archive:
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))

        if manifest.get("format") != PACKAGE_FORMAT:
            raise ValueError(
                f"unsupported LabScript package format: {manifest.get('format')}"
            )

        for name, expected in manifest.get("files", {}).items():
            payload = archive.read(f"src/{name}")
            actual = hashlib.sha256(payload).hexdigest()
            if actual != expected:
                raise ValueError(f"package hash mismatch: {name}")

    return manifest


def run_package(path, runtime):
    path = Path(path)
    manifest = verify_package(path)

    with tempfile.TemporaryDirectory(prefix="labscript-") as temp_dir:
        temp_dir = Path(temp_dir)

        with zipfile.ZipFile(path, "r") as archive:
            archive.extractall(temp_dir)

        source_dir = temp_dir / "src"
        runtime.module_paths.insert(0, source_dir)
        try:
            runtime.execute_file(source_dir / manifest["main"])
        finally:
            runtime.module_paths.pop(0)

    return runtime
