"""Notas rápidas em linha de comando, salvas em arquivo JSON."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def carregar(caminho: Path) -> List[Dict[str, Any]]:
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return []


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Notas rápidas.")
    p.add_argument("--arquivo", default="notas.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("nova")
    n.add_argument("texto")
    n.add_argument("--tags", nargs="*", default=[])
    sub.add_parser("listar").add_argument("--tag")
    sub.add_parser("buscar").add_argument("termo")
    a = p.parse_args(argv)

    caminho = Path(a.arquivo)
    notas = carregar(caminho)
    if a.cmd == "nova":
        notas.append({"id": len(notas) + 1, "texto": a.texto, "tags": a.tags})
        caminho.write_text(json.dumps(notas, ensure_ascii=False), encoding="utf-8")
        print(f"nota {len(notas)} salva")
        return 0
    if a.cmd == "listar":
        achadas = [x for x in notas if not a.tag or a.tag in x["tags"]]
    else:
        achadas = [x for x in notas if a.termo.lower() in x["texto"].lower()]
    for x in achadas:
        tags = f" #{' #'.join(x['tags'])}" if x["tags"] else ""
        print(f"{x['id']}: {x['texto']}{tags}")
    return 0 if achadas else 1


if __name__ == "__main__":
    sys.exit(main())
