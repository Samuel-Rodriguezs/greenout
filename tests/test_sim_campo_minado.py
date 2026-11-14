import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_campo_minado import CampoMinado


class TestCampoMinado(unittest.TestCase):
    def test_primeiro_clique_seguro(self):
        for seed in range(20):
            c = CampoMinado(5, 5, 10, random.Random(seed))
            c.revelar((2, 2))
            self.assertFalse(c.perdeu)
            self.assertEqual(len(c.minas), 10)

    def test_determinismo(self):
        a = CampoMinado(rng=random.Random(3))
        b = CampoMinado(rng=random.Random(3))
        a.revelar((0, 0))
        b.revelar((0, 0))
        self.assertEqual(a.minas, b.minas)

    def test_flood_fill(self):
        c = CampoMinado(5, 5, 1, random.Random(1))
        c.revelar((2, 2))
        self.assertGreater(len(c.reveladas), 1)
        self.assertTrue(all(p not in c.minas for p in c.reveladas))

    def test_perder_ao_pisar_em_mina(self):
        c = CampoMinado(4, 4, 3, random.Random(1))
        c.revelar((0, 0))
        mina = next(iter(c.minas))
        c.revelar(mina)
        self.assertTrue(c.perdeu)

    def test_vencer(self):
        c = CampoMinado(4, 4, 3, random.Random(2))
        c.revelar((0, 0))
        for l in range(4):
            for k in range(4):
                if (l, k) not in c.minas:
                    c.revelar((l, k))
        self.assertTrue(c.venceu)

    def test_bandeira_protege(self):
        c = CampoMinado(4, 4, 3, random.Random(1))
        c.revelar((0, 0))
        mina = next(iter(c.minas))
        c.alternar_bandeira(mina)
        c.revelar(mina)
        self.assertFalse(c.perdeu)
        c.alternar_bandeira(mina)
        self.assertNotIn(mina, c.bandeiras)

    def test_contagem_e_render(self):
        c = CampoMinado(3, 3, 1, random.Random(1))
        c._iniciado = True
        c.minas = {(0, 0)}
        self.assertEqual(c.contagem((1, 1)), 1)
        c.revelar((2, 2))
        self.assertEqual(c.render()[2], "   ")
        self.assertEqual(c.render()[0][0], "#")
        self.assertEqual(c.render()[1][1], "1")

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            CampoMinado(2, 2, 4)
        with self.assertRaises(ValueError):
            CampoMinado(3, 3, 1).revelar((5, 5))


if __name__ == "__main__":
    unittest.main()
