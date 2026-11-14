"""Gerenciador de tarefas com persistencia em JSON."""
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Union


@dataclass
class Tarefa:
    id: int
    titulo: str
    concluida: bool = False


class GerenciadorTarefas:
    def __init__(self, caminho: Union[str, Path]) -> None:
        self.caminho = Path(caminho)
        self.tarefas: List[Tarefa] = []
        if self.caminho.exists():
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
            self.tarefas = [Tarefa(**d) for d in dados]

    def _salvar(self) -> None:
        self.caminho.write_text(
            json.dumps([asdict(t) for t in self.tarefas], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _buscar(self, id_: int) -> Tarefa:
        for t in self.tarefas:
            if t.id == id_:
                return t
        raise KeyError(f"tarefa {id_} nao encontrada")

    def adicionar(self, titulo: str) -> Tarefa:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("titulo vazio")
        novo_id = max((t.id for t in self.tarefas), default=0) + 1
        tarefa = Tarefa(novo_id, titulo)
        self.tarefas.append(tarefa)
        self._salvar()
        return tarefa

    def concluir(self, id_: int) -> None:
        self._buscar(id_).concluida = True
        self._salvar()

    def remover(self, id_: int) -> None:
        self.tarefas.remove(self._buscar(id_))
        self._salvar()

    def pendentes(self) -> List[Tarefa]:
        return [t for t in self.tarefas if not t.concluida]
