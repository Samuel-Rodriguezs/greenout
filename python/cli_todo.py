"""Lista de tarefas em linha de comando com persistência em JSON."""
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


def carregar(caminho: Path) -> List[Dict[str, Any]]:
    if not caminho.exists():
        return []
    return json.loads(caminho.read_text(encoding="utf-8"))


def salvar(caminho: Path, tarefas: List[Dict[str, Any]]) -> None:
    caminho.write_text(json.dumps(tarefas, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Gerenciador de tarefas.")
    p.add_argument("--arquivo", default="todo.json")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("texto")
    sub.add_parser("list").add_argument("--pendentes", action="store_true")
    sub.add_parser("done").add_argument("id", type=int)
    sub.add_parser("rm").add_argument("id", type=int)
    a = p.parse_args(argv)

    caminho = Path(a.arquivo)
    tarefas = carregar(caminho)
    if a.cmd == "add":
        novo = max((t["id"] for t in tarefas), default=0) + 1
        tarefas.append({"id": novo, "texto": a.texto, "feita": False})
        salvar(caminho, tarefas)
        print(f"tarefa {novo} adicionada")
    elif a.cmd == "list":
        for t in tarefas:
            if a.pendentes and t["feita"]:
                continue
            print(f"{t['id']}. [{'x' if t['feita'] else ' '}] {t['texto']}")
    else:
        alvo = next((t for t in tarefas if t["id"] == a.id), None)
        if alvo is None:
            print(f"erro: tarefa {a.id} não encontrada", file=sys.stderr)
            return 1
        if a.cmd == "done":
            alvo["feita"] = True
            print(f"tarefa {a.id} concluída")
        else:
            tarefas.remove(alvo)
            print(f"tarefa {a.id} removida")
        salvar(caminho, tarefas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
