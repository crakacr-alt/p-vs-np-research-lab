import io
import tempfile
import unittest
from pathlib import Path

from pnp_lab.labscript.language import Language, detect_language, translate_source
from pnp_lab.labscript.runtime import LabRuntime, LabScriptError, StepLimitError
from pnp_lab.labscript.stdlib import ModuleNamespace


class LabScriptLanguageTests(unittest.TestCase):
    def run_program(self, source):
        output = io.StringIO()
        runtime = LabRuntime(output=output)
        runtime.execute(source)
        return output.getvalue(), runtime

    def test_english_program(self):
        source = '''LangRule="-ENG"

let total = 0
function square(x):
    return x * x

for i in range(1, 5):
    total += square(i)

print(total)
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "30\n")

    def test_russian_program(self):
        source = '''Язык="-РУС"

пусть итог = 0
функция квадрат(x):
    вернуть x * x

для i в диапазон(1, 5):
    итог += квадрат(i)

печать(итог)
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "30\n")

    def test_russian_else_if_phrase(self):
        source = '''Язык="-РУС"
пусть x = 2
если x == 1:
    печать("one")
иначе если x == 2:
    печать("two")
иначе:
    печать("other")
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "two\n")

    def test_strings_are_not_keyword_translated(self):
        source = '''Язык="-РУС"
печать("если иначе функция")
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "если иначе функция\n")

    def test_function_assignment_is_local(self):
        source = '''LangRule="-ENG"
let x = 10
function work():
    x = 20
    return x
print(work())
print(x)
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "20\n10\n")

    def test_math_crypto_and_sat_modules(self):
        source = '''LangRule="-ENG"
import math
import crypto
import sat
print(round(math.sqrt(81)))
print(crypto.decode64(crypto.encode64("hello")))
result = sat.solve(1, [[1], [-1]])
print(result["sat"])
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "9\nhello\nFalse\n")

    def test_russian_module_names(self):
        source = '''Язык="-РУС"
импорт математика
импорт крипто
печать(округлить(математика.sqrt(16)))
печать(крипто.decode64(крипто.encode64("привет")))
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "4\nпривет\n")

    def test_standard_list_and_json_helpers(self):
        source = '''Язык="-РУС"
пусть данные = []
для i в диапазон(3):
    добавить(данные, i * i)
пусть текст = json_код(данные)
печать(текст)
печать(длина(json_декод(текст)))
'''
        output, _ = self.run_program(source)
        self.assertEqual(output, "[0, 1, 4]\n3\n")

    def test_local_lab_module(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            (temp / "helper.lab").write_text(
                'LangRule="-ENG"\nfunction triple(x):\n    return x * 3\n',
                encoding="utf-8",
            )
            main = temp / "main.lab"
            main.write_text(
                'LangRule="-ENG"\nimport helper\nprint(helper.triple(7))\n',
                encoding="utf-8",
            )

            output = io.StringIO()
            runtime = LabRuntime(output=output)
            runtime.execute_file(main)
            self.assertEqual(output.getvalue(), "21\n")

    def test_explicit_host_module_embedding(self):
        output = io.StringIO()
        company = ModuleNamespace(
            "company",
            {"price_with_tax": lambda value: round(value * 1.2, 2)},
        )
        runtime = LabRuntime(output=output, modules={"company": company})
        runtime.execute(
            'LangRule="-ENG"\nimport company\nprint(company.price_with_tax(100))\n'
        )
        self.assertEqual(output.getvalue(), "120.0\n")

    def test_python_object_attributes_are_blocked(self):
        with self.assertRaises(LabScriptError):
            self.run_program('LangRule="-ENG"\nprint((1).__class__)\n')

    def test_step_limit_stops_infinite_loop(self):
        runtime = LabRuntime(max_steps=20)
        with self.assertRaises(StepLimitError):
            runtime.execute('LangRule="-ENG"\nwhile true:\n    pass\n')

    def test_language_directives(self):
        lang, _ = detect_language('LangRule="-ENG"\nprint(1)\n')
        self.assertEqual(lang, Language.ENG)
        lang, _ = detect_language('Язык="-РУС"\nпечать(1)\n')
        self.assertEqual(lang, Language.RUS)

    def test_translation_keeps_line_count(self):
        source = 'Язык="-РУС"\nпусть x = 1\nпечать(x)\n'
        _, translated = translate_source(source)
        self.assertEqual(len(source.splitlines()), len(translated.splitlines()))


if __name__ == "__main__":
    unittest.main()
