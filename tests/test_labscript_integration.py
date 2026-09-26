import io
import tempfile
import unittest
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


if __name__ == "__main__":
    unittest.main()
