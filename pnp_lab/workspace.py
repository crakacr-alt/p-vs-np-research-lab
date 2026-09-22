import os
from pathlib import Path


def get_workspace_root() -> Path:
    """Возвращает каталог, внутри которого MCP разрешено работать с файлами."""

    configured = os.environ.get("PNP_LAB_WORKSPACE")

    if configured:
        return Path(configured).expanduser().resolve()

    return Path.cwd().resolve()


def safe_workspace_path(path: str | Path) -> Path:
    """Не позволяет MCP читать файлы за пределами workspace."""

    root = get_workspace_root()
    requested = Path(path).expanduser()

    if requested.is_absolute():
        candidate = requested.resolve()
    else:
        candidate = (root / requested).resolve()

    if candidate != root and root not in candidate.parents:
        raise ValueError(
            "Путь находится вне PNP_LAB_WORKSPACE. "
            "Укажите файл внутри разрешённого рабочего каталога."
        )

    return candidate
