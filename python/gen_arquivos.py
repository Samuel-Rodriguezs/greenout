"""Geração de arquivos CSV e JSON Lines de dados fictícios em diretórios temporários."""
from __future__ import annotations

import csv
import json
import tempfile
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


def _para_dict(obj: Any) -> dict[str, Any]:
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, dict):
        return dict(obj)
    raise TypeError(f"não serializável como linha: {type(obj).__name__}")


def _json_padrao(o: Any) -> str:
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    raise TypeError(f"tipo não serializável: {type(o).__name__}")


def _achatar(d: dict[str, Any], prefixo: str = "") -> dict[str, Any]:
    """{'a': {'b': 1}} -> {'a.b': 1}, para caber em colunas de CSV."""
    saida: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, dict):
            saida.update(_achatar(v, f"{prefixo}{k}."))
        else:
            saida[f"{prefixo}{k}"] = v.isoformat() if isinstance(v, (date, datetime)) else v
    return saida


def escrever_csv(linhas: Iterable[Any], destino: Path) -> int:
    """CSV UTF-8 com cabeçalho (colunas = união ordenada de chaves achatadas). Devolve nº de linhas."""
    registros = [_achatar(_para_dict(x)) for x in linhas]
    colunas: list[str] = []
    for r in registros:
        for k in r:
            if k not in colunas:
                colunas.append(k)
    with open(destino, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, restval="")
        w.writeheader()
        w.writerows(registros)
    return len(registros)


def escrever_jsonl(linhas: Iterable[Any], destino: Path) -> int:
    n = 0
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        for x in linhas:
            f.write(json.dumps(_para_dict(x), ensure_ascii=False, default=_json_padrao))
            f.write("\n")
            n += 1
    return n


def ler_csv(origem: Path) -> list[dict[str, str]]:
    with open(origem, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ler_jsonl(origem: Path) -> list[dict[str, Any]]:
    with open(origem, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def gerar_em_tempdir(linhas: list[Any], nome_base: str = "dados") -> tuple[tempfile.TemporaryDirectory, Path, Path]:
    """Cria `<nome_base>.csv` e `<nome_base>.jsonl` num diretório temporário.

    O chamador deve manter o TemporaryDirectory vivo (ou chamar .cleanup())."""
    tmp = tempfile.TemporaryDirectory(prefix="gen_arquivos_")
    base = Path(tmp.name)
    csv_path, jsonl_path = base / f"{nome_base}.csv", base / f"{nome_base}.jsonl"
    escrever_csv(linhas, csv_path)
    escrever_jsonl(linhas, jsonl_path)
    return tmp, csv_path, jsonl_path
