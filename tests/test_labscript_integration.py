import hashlib
import io
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from pnp_lab.labscript.markdown import build_markdown_report, execute_markdown
from pnp_lab.labscript.package import build_package, run_package, verify_package
from pnp_lab.labscript.runtime import LabRuntime


class LabScriptIntegrationTests(unittest.TestCase):
    def test_build_verify_and_run_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            main = temp / "main.lab"
            helper = temp / "helper.lab"
            main.write_text(
                'LangRule="-ENG"\nimport helper\nprint(helper.answer())\n',
                encoding="utf-8",
            )
            helper.write_text(
                'LangRule="-ENG"\nfunction answer():\n    return 42\n',
                encoding="utf-8",
            )

            package, manifest = build_package(main)
            self.assertEqual(manifest["main"], "main.lab")
            self.assertTrue(package.is_file())
            self.assertEqual(verify_package(package)["files"], manifest["files"])

            output = io.StringIO()
            runtime = LabRuntime(output=output)
            run_package(package, runtime)
            self.assertEqual(output.getvalue(), "42\n")

    def test_markdown_blocks_share_runtime_state(self):
        text = '''# Note

```lab
Язык="-РУС"
пусть x = 20
```

```labscript
Язык="-РУС"
печать(x + 22)
```
'''
        blocks = execute_markdown(text)
        self.assertEqual(blocks, ["", "42\n"])

    def test_markdown_report_does_not_modify_note(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            note = temp / "note.md"
            original = '# Test\n\n```lab\nprint(2 + 2)\n```\n'
            note.write_text(original, encoding="utf-8")

            report, blocks = build_markdown_report(note)

            self.assertEqual(note.read_text(encoding="utf-8"), original)
            self.assertEqual(blocks, ["4\n"])
            self.assertIn("4", report.read_text(encoding="utf-8"))

    def test_build_is_deterministic_and_ignores_unused_modules(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            main = temp / "main.lab"
            helper = temp / "helper.lab"
            unused = temp / "unused.lab"
            main.write_text(
                'LangRule="-ENG"\nimport helper\nprint(helper.answer())\n',
                encoding="utf-8",
            )
            helper.write_text(
                'LangRule="-ENG"\nfunction answer():\n    return 42\n',
                encoding="utf-8",
            )
            unused.write_text('print("do not package me")\n', encoding="utf-8")

            first = temp / "first.labpkg"
            second = temp / "second.labpkg"
            _, manifest = build_package(main, first)
            os.utime(main, None)
            build_package(main, second)

            self.assertNotIn("unused.lab", manifest["files"])
            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )

    def test_unsafe_package_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            package = Path(temp_dir) / "bad.labpkg"
            payload = b'print(1)\n'
            manifest = {
                "format": 1,
                "labscript_version": "0.1",
                "main": "../evil.lab",
                "language": "ENG",
                "files": {
                    "../evil.lab": hashlib.sha256(payload).hexdigest(),
                },
            }

            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr(
                    "manifest.json",
                    json.dumps(manifest).encode("utf-8"),
                )
                archive.writestr("src/../evil.lab", payload)

            with self.assertRaises(ValueError):
                verify_package(package)


if __name__ == "__main__":
    unittest.main()
