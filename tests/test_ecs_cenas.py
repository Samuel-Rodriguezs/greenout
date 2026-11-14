import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_cenas import Cena, PilhaCenas


class Gravadora(Cena):
    def __init__(self, nome, log, transparente=False):
        self.nome, self.log = nome, log
        self.transparente_update = transparente

    def entrar(self): self.log.append(f"{self.nome}:entrar")
    def sair(self): self.log.append(f"{self.nome}:sair")
    def pausar(self): self.log.append(f"{self.nome}:pausar")
    def retomar(self): self.log.append(f"{self.nome}:retomar")
    def atualizar(self, dt): self.log.append(f"{self.nome}:upd")


class TestPilha(unittest.TestCase):
    def test_empilhar_desempilhar(self):
        log = []
        p = PilhaCenas()
        p.empilhar(Gravadora("jogo", log))
        p.empilhar(Gravadora("menu", log))
        p.desempilhar()
        self.assertEqual(log, ["jogo:entrar", "jogo:pausar", "menu:entrar", "menu:sair", "jogo:retomar"])
        self.assertEqual(len(p), 1)

    def test_atualiza_so_topo(self):
        log = []
        p = PilhaCenas()
        p.empilhar(Gravadora("a", log))
        p.empilhar(Gravadora("b", log))
        log.clear()
        p.atualizar(0.1)
        self.assertEqual(log, ["b:upd"])

    def test_transparente_propaga(self):
        log = []
        p = PilhaCenas()
        p.empilhar(Gravadora("a", log))
        p.empilhar(Gravadora("hud", log, transparente=True))
        log.clear()
        p.atualizar(0.1)
        self.assertEqual(log, ["hud:upd", "a:upd"])

    def test_trocar(self):
        log = []
        p = PilhaCenas()
        p.empilhar(Gravadora("a", log))
        log.clear()
        p.trocar(Gravadora("b", log))
        self.assertEqual(log, ["a:sair", "b:entrar"])
        self.assertEqual(p.nomes(), ["Gravadora"])

    def test_vazia(self):
        p = PilhaCenas()
        self.assertIsNone(p.topo)
        with self.assertRaises(IndexError):
            p.desempilhar()
        p.atualizar(1)


if __name__ == "__main__":
    unittest.main()
