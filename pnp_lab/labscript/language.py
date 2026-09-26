import io
import re
import tokenize
from enum import Enum


class Language(str, Enum):
    ENG = "ENG"
    RUS = "RUS"


_DIRECTIVE_RE = re.compile(
    r'^\s*(?:LangRule|Language|Язык)\s*=\s*["\']-?(ENG|EN|RUS|RU|РУС|АНГ)["\']\s*$',
    re.IGNORECASE,
)

_RUS_KEYWORDS = {
    "функция": "def",
    "вернуть": "return",
    "если": "if",
    "иначеесли": "elif",
    "иначе": "else",
    "пока": "while",
    "для": "for",
    "в": "in",
    "прервать": "break",
    "продолжить": "continue",
    "пропустить": "pass",
    "истина": "True",
    "ложь": "False",
    "пусто": "None",
    "и": "and",
    "или": "or",
    "не": "not",
    "импорт": "import",
    "из": "from",
    "как": "as",
}

_ENG_KEYWORDS = {
    "function": "def",
    "elseif": "elif",
    "true": "True",
    "false": "False",
    "null": "None",
}

_RUS_BUILTINS = {
    "печать": "print",
    "длина": "length",
    "диапазон": "range",
    "сумма": "sum",
    "минимум": "min",
    "максимум": "max",
    "абс": "abs",
    "округлить": "round",
    "хэш": "hash",
    "код64": "encode64",
    "декод64": "decode64",
    "решить_sat": "solve_sat",
    "проверить": "assert_true",
    "тип": "type_name",
    "добавить": "append",
    "верхний": "upper",
    "нижний": "lower",
    "разделить": "split",
    "соединить": "join",
    "json_код": "json_encode",
    "json_декод": "json_decode",
}

_RUS_MODULES = {
    "математика": "math",
    "крипто": "crypto",
    "сат": "sat",
}


def detect_language(source: str) -> tuple[Language, str]:
    """Определяет язык и удаляет директиву из первой содержательной строки."""

    lines = source.splitlines()
    first_content = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            first_content = index
            break

    if first_content is None:
        return Language.ENG, source

    match = _DIRECTIVE_RE.match(lines[first_content])
    if match:
        raw = match.group(1).upper()
        language = Language.RUS if raw in {"RUS", "RU", "РУС"} else Language.ENG
        lines[first_content] = ""
        return language, "\n".join(lines)

    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in tokens:
            if (
                token.type == tokenize.NAME
                and token.string.lower() in _RUS_KEYWORDS
            ):
                return Language.RUS, source
    except tokenize.TokenError:
        pass

    return Language.ENG, source


def _add_edit(edits, line, start, end, replacement):
    edits.setdefault(line, []).append((start, end, replacement))


def _apply_edits(source, edits):
    lines = source.splitlines(keepends=True)

    for line_number, line_edits in edits.items():
        index = line_number - 1
        if index < 0 or index >= len(lines):
            continue

        line = lines[index]
        for start, end, replacement in sorted(
            line_edits,
            key=lambda item: item[0],
            reverse=True,
        ):
            line = line[:start] + replacement + line[end:]
        lines[index] = line

    return "".join(lines)


def translate_source(source: str) -> tuple[Language, str]:
    """Нормализует LabScript keywords, не меняя строки и комментарии."""

    language, body = detect_language(source)
    keyword_map = _RUS_KEYWORDS if language == Language.RUS else _ENG_KEYWORDS
    name_map = {}

    if language == Language.RUS:
        name_map.update(_RUS_BUILTINS)
        name_map.update(_RUS_MODULES)

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(body).readline))
    except tokenize.TokenError:
        # ast.parse ниже сформирует основную syntax diagnostic.
        return language, body

    edits = {}
    let_word = "пусть" if language == Language.RUS else "let"
    phrase_first = "иначе" if language == Language.RUS else "else"
    phrase_second = "если" if language == Language.RUS else "if"

    index = 0
    while index < len(tokens):
        token = tokens[index]

        if token.type != tokenize.NAME:
            index += 1
            continue

        lowered = token.string.lower()

        # "иначе если" / "else if" считаем одним keyword. Работаем по token
        # positions, поэтому такая фраза внутри string/comment не затрагивается.
        if (
            lowered == phrase_first
            and index + 1 < len(tokens)
            and tokens[index + 1].type == tokenize.NAME
            and tokens[index + 1].string.lower() == phrase_second
            and tokens[index + 1].start[0] == token.start[0]
        ):
            second = tokens[index + 1]
            _add_edit(
                edits,
                token.start[0],
                token.start[1],
                second.end[1],
                "elif",
            )
            index += 2
            continue

        # let/пусть — синтаксический сахар. Удаляем keyword и пробелы до
        # следующего identifier, но только когда tokenizer видит настоящий NAME.
        if lowered == let_word:
            end = token.end[1]
            if (
                index + 1 < len(tokens)
                and tokens[index + 1].start[0] == token.start[0]
            ):
                end = tokens[index + 1].start[1]
            _add_edit(edits, token.start[0], token.start[1], end, "")
            index += 1
            continue

        replacement = keyword_map.get(lowered)
        if replacement is None:
            replacement = name_map.get(lowered)

        if replacement is not None:
            _add_edit(
                edits,
                token.start[0],
                token.start[1],
                token.end[1],
                replacement,
            )

        index += 1

    return language, _apply_edits(body, edits)
