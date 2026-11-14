import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_rubik_2x2 import (MOVIMENTOS, RESOLVIDO, aplicar, aplicar_sequencia,
                           inverso, resolver, valido)


class TestRubik2x2(unittest.TestCase):
    def test_quatro_quartos_de_volta_sao_identidade(self):
        for face in "URF":
            self.assertEqual(aplicar_sequencia(RESOLVIDO, [face] * 4), RESOLVIDO)

    def test_inverso_desfaz(self):
        for m in MOVIMENTOS:
            self.assertEqual(aplicar(aplicar(RESOLVIDO, m), inverso(m)), RESOLVIDO)

    def test_movimentos_mantem_estado_valido(self):
        e = RESOLVIDO
        rng = random.Random(5)
        for _ in range(50):
            e = aplicar(e, rng.choice(MOVIMENTOS))
            self.assertTrue(valido(e))

    def test_ordem_de_sexy_move(self):
        # R U R' U' tem ordem 6 no cubo 2x2
        seq = ["R", "U", "R'", "U'"]
        e = RESOLVIDO
        for i in range(1, 7):
            e = aplicar_sequencia(e, seq)
            self.assertEqual(e == RESOLVIDO, i == 6, i)

    def test_ja_resolvido(self):
        self.assertEqual(resolver(RESOLVIDO), [])

    def test_um_movimento(self):
        self.assertEqual(resolver(aplicar(RESOLVIDO, "R")), ["R'"])

    def test_embaralhado_curto_resolve_com_no_maximo_o_embaralho(self):
        rng = random.Random(2)
        for _ in range(3):
            embaralho = [rng.choice(MOVIMENTOS) for _ in range(7)]
            e = aplicar_sequencia(RESOLVIDO, embaralho)
            sol = resolver(e)
            self.assertIsNotNone(sol)
            self.assertLessEqual(len(sol), 7)
            self.assertEqual(aplicar_sequencia(e, sol), RESOLVIDO)

    def test_estado_invalido_sem_solucao(self):
        perm, ori = RESOLVIDO
        torcido = (perm, (1,) + ori[1:])  # soma de torções != 0 mod 3
        self.assertFalse(valido(torcido))
        self.assertIsNone(resolver(torcido))


if __name__ == "__main__":
    unittest.main()
