import json
import os
import tempfile
from pathlib import Path
from typing import Any


def ler_json(caminho: str | Path) -> Any:
    """Lê um arquivo JSON UTF-8. Levanta FileNotFoundError ou ValueError."""
    caminho = Path(caminho)
    with caminho.open(encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido em {caminho}: {e}") from e


def escrever_json(caminho: str | Path, dados: Any, indent: int = 2) -> None:
    """Escreve JSON de forma atômica (arquivo temporário + replace)."""
    caminho = Path(caminho)
    fd, tmp = tempfile.mkstemp(dir=caminho.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=indent)
        os.replace(tmp, caminho)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
