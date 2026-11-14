import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_mediator import SalaChat, Usuario


class TestMediator(unittest.TestCase):
    def setUp(self):
        self.sala = SalaChat()
        self.a, self.b, self.c = Usuario("ana"), Usuario("beto"), Usuario("cris")
        for u in (self.a, self.b, self.c):
            self.sala.entrar(u)

    def test_broadcast_exclui_remetente(self):
        self.a.falar("oi")
        self.assertIn(("ana", "oi"), self.b.recebidas)
        self.assertIn(("ana", "oi"), self.c.recebidas)
        self.assertNotIn(("ana", "oi"), self.a.recebidas)

    def test_privada(self):
        self.a.sussurrar("beto", "segredo")
        self.assertIn(("ana", "segredo"), self.b.recebidas)
        self.assertNotIn(("ana", "segredo"), self.c.recebidas)

    def test_entrada_notifica(self):
        self.assertIn(("sistema", "cris entrou"), self.a.recebidas)

    def test_saida(self):
        self.sala.sair(self.c)
        self.assertIsNone(self.c.sala)
        with self.assertRaises(RuntimeError):
            self.c.falar("x")
        self.assertIn(("sistema", "cris saiu"), self.a.recebidas)

    def test_nome_duplicado_e_destino_inexistente(self):
        with self.assertRaises(ValueError):
            self.sala.entrar(Usuario("ana"))
        with self.assertRaises(KeyError):
            self.a.sussurrar("zé", "x")


if __name__ == "__main__":
    unittest.main()
