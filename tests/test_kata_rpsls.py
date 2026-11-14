import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_rpsls import REGRAS, descricao, jogar

JOGADAS = list(REGRAS)


class TestKataRpsls(unittest.TestCase):
    def test_empates(self):
        for j in JOGADAS:
            self.assertEqual(jogar(j, j), "empate")

    def test_regras_oficiais(self):
        vitorias = [
            ("tesoura", "papel"), ("papel", "pedra"), ("pedra", "lagarto"),
            ("lagarto", "spock"), ("spock", "tesoura"), ("tesoura", "lagarto"),
            ("lagarto", "papel"), ("papel", "spock"), ("spock", "pedra"),
            ("pedra", "tesoura"),
        ]
        for vencedor, perdedor in vitorias:
            self.assertEqual(jogar(vencedor, perdedor), "jogador 1")
            self.assertEqual(jogar(perdedor, vencedor), "jogador 2")

    def test_cada_jogada_vence_duas_e_perde_duas(self):
        for j in JOGADAS:
            vence = [o for o in JOGADAS if o != j and jogar(j, o) == "jogador 1"]
            perde = [o for o in JOGADAS if o != j and jogar(j, o) == "jogador 2"]
            self.assertEqual(len(vence), 2)
            self.assertEqual(len(perde), 2)

    def test_descricao(self):
        self.assertEqual(descricao("tesoura", "papel"), "tesoura corta papel")
        self.assertEqual(descricao("pedra", "spock"), "spock vaporiza pedra")
        self.assertEqual(descricao("pedra", "pedra"), "pedra empata com pedra")

    def test_case_insensitive(self):
        self.assertEqual(jogar("PEDRA", "Tesoura"), "jogador 1")

    def test_invalida(self):
        with self.assertRaises(ValueError):
            jogar("fogo", "pedra")


if __name__ == "__main__":
    unittest.main()
