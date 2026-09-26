"""LabScript — простой двуязычный язык Research Lab."""

from .language import Language, detect_language, translate_source
from .runtime import LabRuntime, LabScriptError, run_source

LABSCRIPT_VERSION = "0.1"

__all__ = [
    "LABSCRIPT_VERSION",
    "LabRuntime",
    "LabScriptError",
    "Language",
    "detect_language",
    "run_source",
    "translate_source",
]
