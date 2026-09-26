import argparse
import hashlib
import io
import sys
from pathlib import Path

from .language import detect_language
from .markdown import build_markdown_report
from .package import build_package, run_package, verify_package
from .runtime import LabRuntime, LabScriptError, parse_source
from .stdlib import decode64, encode64


def _runtime(max_steps, debug=False):
    trace = None

    if debug:
        def trace(event):
            line = event["line"]
            node = event["node"]
            steps = event["steps"]
            local_values = event["locals"]
            print(
                f"[step {steps:05d}] line={line} node={node} locals={local_values}",
                file=sys.stderr,
            )

    return LabRuntime(output=sys.stdout, max_steps=max_steps, trace=trace)


def run_command(args):
    runtime = _runtime(args.max_steps)
    path = Path(args.file)

    if path.suffix == ".labpkg":
        run_package(path, runtime)
    else:
        runtime.execute_file(path)


def check_command(args):
    path = Path(args.file)

    if path.suffix == ".labpkg":
        manifest = verify_package(path)
        print(f"OK package format={manifest['format']} main={manifest['main']}")
        return

    source = path.read_text(encoding="utf-8")
    language, _, tree = parse_source(source, filename=str(path))
    print(f"OK language={language.value} statements={len(tree.body)}")


def debug_command(args):
    runtime = _runtime(args.max_steps, debug=True)
    runtime.execute_file(args.file)


def build_command(args):
    path, manifest = build_package(args.file, args.output)
    print(f"built: {path}")
    print(f"language: {manifest['language']}")
    print(f"files: {len(manifest['files'])}")


def verify_command(args):
    manifest = verify_package(args.file)
    print(f"OK package format={manifest['format']}")
    print(f"main: {manifest['main']}")
    print(f"files: {len(manifest['files'])}")


def hash_command(args):
    digest = hashlib.new(args.algorithm.lower())

    if args.file:
        with Path(args.value).open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
    else:
        digest.update(args.value.encode("utf-8"))

    print(digest.hexdigest())


def encode_command(args):
    print(encode64(args.value))


def decode_command(args):
    print(decode64(args.value))


def markdown_command(args):
    output, blocks = build_markdown_report(args.file, args.output)
    print(f"blocks: {len(blocks)}")
    print(f"report: {output}")


def new_command(args):
    path = Path(args.file)
    if path.exists() and not args.force:
        raise LabScriptError(f"file already exists: {path}")

    language = args.lang.upper()
    if language == "RUS":
        source = (
            'Язык="-РУС"\n\n'
            'функция квадрат(x):\n'
            '    вернуть x * x\n\n'
            'для i в диапазон(1, 6):\n'
            '    печать(i, квадрат(i))\n'
        )
    else:
        source = (
            'LangRule="-ENG"\n\n'
            'function square(x):\n'
            '    return x * x\n\n'
            'for i in range(1, 6):\n'
            '    print(i, square(i))\n'
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    print(f"created: {path}")


def info_command(args):
    source = Path(args.file).read_text(encoding="utf-8")
    language, _ = detect_language(source)
    print(f"language: {language.value}")
    print("runtime: LabScript")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="labscript",
        description="LabScript — bilingual language for P vs NP Research Lab",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="run .lab or .labpkg")
    run_parser.add_argument("file")
    run_parser.add_argument("--max-steps", type=int, default=1_000_000)
    run_parser.set_defaults(handler=run_command)

    check_parser = commands.add_parser("check", help="check syntax without running")
    check_parser.add_argument("file")
    check_parser.set_defaults(handler=check_command)

    debug_parser = commands.add_parser("debug", help="run with statement trace")
    debug_parser.add_argument("file")
    debug_parser.add_argument("--max-steps", type=int, default=100_000)
    debug_parser.set_defaults(handler=debug_command)

    build_parser = commands.add_parser("build", help="build portable .labpkg")
    build_parser.add_argument("file")
    build_parser.add_argument("-o", "--output")
    build_parser.set_defaults(handler=build_command)

    verify_parser = commands.add_parser("verify", help="verify .labpkg hashes")
    verify_parser.add_argument("file")
    verify_parser.set_defaults(handler=verify_command)

    hash_parser = commands.add_parser("hash", help="hash text or file")
    hash_parser.add_argument("value")
    hash_parser.add_argument("--algorithm", default="sha256")
    hash_parser.add_argument("--file", action="store_true")
    hash_parser.set_defaults(handler=hash_command)

    encode_parser = commands.add_parser("encode64", help="Base64 encode UTF-8 text")
    encode_parser.add_argument("value")
    encode_parser.set_defaults(handler=encode_command)

    decode_parser = commands.add_parser("decode64", help="Base64 decode UTF-8 text")
    decode_parser.add_argument("value")
    decode_parser.set_defaults(handler=decode_command)

    markdown_parser = commands.add_parser(
        "markdown",
        help="run lab/labscript blocks from Markdown or Obsidian note",
    )
    markdown_parser.add_argument("file")
    markdown_parser.add_argument("-o", "--output")
    markdown_parser.set_defaults(handler=markdown_command)

    new_parser = commands.add_parser("new", help="create a starter .lab program")
    new_parser.add_argument("file")
    new_parser.add_argument("--lang", choices=["ENG", "RUS"], default="ENG")
    new_parser.add_argument("--force", action="store_true")
    new_parser.set_defaults(handler=new_command)

    info_parser = commands.add_parser("info", help="show detected source language")
    info_parser.add_argument("file")
    info_parser.set_defaults(handler=info_command)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        args.handler(args)
    except (LabScriptError, ValueError, OSError) as error:
        print(f"LabScript error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
