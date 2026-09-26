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

    # Без директивы не угадываем смысл программы агрессивно.
    # Русские управляющие слова — достаточно сильный сигнал.
    lowered = source.lower()
    if any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in _RUS_KEYWORDS):
        return Language.RUS, source

    return Language.ENG, source


def _remove_let_prefix(source: str, language: Language) -> str:
    word = "пусть" if language == Language.RUS else "let"
    pattern = re.compile(rf"^(\s*){word}\s+([\w\u0400-\u04ff]+\s*=)", re.IGNORECASE)

    lines = []
    for line in source.splitlines():
        lines.append(pattern.sub(r"\1\2", line))
    return "\n".join(lines)


def translate_source(source: str) -> tuple[Language, str]:
    """Переводит ключевые слова LabScript в нейтральный parser syntax.

    Строки и комментарии не изменяются: замены проходят через tokenizer.
    """

    language, body = detect_language(source)
    if language == Language.RUS:
        body = re.sub(r"\bиначе\s+если\b", "иначеесли", body, flags=re.IGNORECASE)

    body = _remove_let_prefix(body, language)

    keyword_map = _RUS_KEYWORDS if language == Language.RUS else _ENG_KEYWORDS
    name_map = {}

    if language == Language.RUS:
        name_map.update(_RUS_BUILTINS)
        name_map.update(_RUS_MODULES)

    tokens = []
    reader = io.StringIO(body).readline

    for token in tokenize.generate_tokens(reader):
        if token.type == tokenize.NAME:
            replacement = keyword_map.get(token.string.lower())
            if replacement is None:
                replacement = name_map.get(token.string.lower())

            if replacement is not None:
                token = tokenize.TokenInfo(
                    token.type,
                    replacement,
                    token.start,
                    token.end,
                    token.line,
                )

        tokens.append(token)

    return language, tokenize.untokenize(tokens)
