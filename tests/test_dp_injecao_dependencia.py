import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_injecao_dependencia import Container


class Relogio:
    def agora(self) -> str:
        return "real"


class RelogioFalso(Relogio):
    def agora(self) -> str:
        return "falso"


class Repo:
    pass


class Servico:
    def __init__(self, relogio: Relogio, repo: Repo, prefixo: str = "svc") -> None:
        self.relogio = relogio
        self.repo = repo
        self.prefixo = prefixo


class TestInjecao(unittest.TestCase):
    def test_resolve_dependencias_aninhadas(self):
        c = Container()
        c.registrar(Relogio, Relogio)
        s = c.resolver(Servico)
        self.assertIsInstance(s.relogio, Relogio)
        self.assertIsInstance(s.repo, Repo)
        self.assertEqual(s.prefixo, "svc")

    def test_troca_implementacao(self):
        c = Container()
        c.registrar(Relogio, RelogioFalso)
        self.assertEqual(c.resolver(Servico).relogio.agora(), "falso")

    def test_singleton(self):
        c = Container()
        c.registrar(Repo, Repo, singleton=True)
        self.assertIs(c.resolver(Servico).repo, c.resolver(Servico).repo)

    def test_transiente_por_padrao(self):
        c = Container()
        c.registrar(Repo, Repo)
        self.assertIsNot(c.resolver(Repo), c.resolver(Repo))

    def test_fabrica_callable(self):
        c = Container()
        r = RelogioFalso()
        c.registrar(Relogio, lambda: r)
        self.assertIs(c.resolver(Servico).relogio, r)


if __name__ == "__main__":
    unittest.main()
