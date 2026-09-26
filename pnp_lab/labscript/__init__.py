"""LabScript — простой двуязычный язык Research Lab."""

from .language import Language, detect_language, translate_source
from .runtime import LabRuntime, LabScriptError, run_source

__all__ = [
    "LabRuntime",
    "LabScriptError",
    "Language",
    "detect_language",
    "run_source",
    "translate_source",
]
