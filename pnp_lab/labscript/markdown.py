import io
import re
from pathlib import Path

from .runtime import LabRuntime


_FENCE_RE = re.compile(
    r"```(?:lab|labscript)\s*\n(.*?)```",
    re.IGNORECASE | re.DOTALL,
)


def execute_markdown(text: str, *, filename="<markdown>"):
    output = io.StringIO()
    runtime = LabRuntime(output=output)
    blocks = []

    for index, match in enumerate(_FENCE_RE.finditer(text), start=1):
        before = output.getvalue()
        runtime.execute(
            match.group(1),
            filename=f"{filename}#block-{index}",
        )
        after = output.getvalue()
        blocks.append(after[len(before):])

    return blocks


def build_markdown_report(path, output_path=None):
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    blocks = execute_markdown(text, filename=str(path))

    lines = [
        f"# LabScript results — {path.name}",
        "",
        "> Generated from LabScript code blocks. Original note is unchanged.",
        "",
    ]

    for index, result in enumerate(blocks, start=1):
        lines.extend(
            [
                f"## Block {index}",
                "",
                "```text",
                result.rstrip(),
                "```",
                "",
            ]
        )

    output_path = Path(
        output_path or path.with_name(path.stem + ".lab-results.md")
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path, blocks
