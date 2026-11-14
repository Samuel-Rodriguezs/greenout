import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_dungeon_bsp import gerar


def regioes(g):
    h, w = len(g), len(g[0])
    vistos, n = set(), 0
    for y in range(h):
        for x in range(w):
            if g[y][x] == 0 and (x, y) not in vistos:
                n += 1
                pilha = [(x, y)]
                vistos.add((x, y))
                while pilha:
                    cx, cy = pilha.pop()
                    for p in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if 0 <= p[0] < w and 0 <= p[1] < h and g[p[1]][p[0]] == 0 and p not in vistos:
                            vistos.add(p)
                            pilha.append(p)
    return n


class TestBSP(unittest.TestCase):
    def test_deterministico(self):
        self.assertEqual(gerar(60, 40, 11), gerar(60, 40, 11))
        self.assertNotEqual(gerar(60, 40, 11)[0], gerar(60, 40, 12)[0])

    def test_conectado_para_varias_seeds(self):
        for seed in range(25):
            g, salas = gerar(60, 40, seed)
            self.assertEqual(regioes(g), 1, f"seed {seed}")
            self.assertGreaterEqual(len(salas), 1)

    def test_salas_dentro_e_sem_sobreposicao(self):
        g, salas = gerar(80, 50, 4)
        self.assertGreater(len(salas), 3)
        for s in salas:
            self.assertTrue(s.x >= 1 and s.y >= 1 and s.x + s.w <= 79 and s.y + s.h <= 49)
            self.assertGreaterEqual(min(s.w, s.h), 4)
            for j in range(s.y, s.y + s.h):
                for i in range(s.x, s.x + s.w):
                    self.assertEqual(g[j][i], 0)
        for i, a in enumerate(salas):
            for b in salas[i + 1:]:
                sep = (a.x + a.w <= b.x or b.x + b.w <= a.x or a.y + a.h <= b.y or b.y + b.h <= a.y)
                self.assertTrue(sep)

    def test_borda_e_parede(self):
        g, _ = gerar(60, 40, 9)
        self.assertTrue(all(g[0][x] == 1 and g[39][x] == 1 for x in range(60)))
        self.assertTrue(all(g[y][0] == 1 and g[y][59] == 1 for y in range(40)))

    def test_mapa_minimo_tem_uma_sala(self):
        g, salas = gerar(6, 6, 1)
        self.assertEqual(len(salas), 1)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            gerar(5, 40, 0)
        with self.assertRaises(ValueError):
            gerar(40, 40, 0, min_sala=2)


if __name__ == "__main__":
    unittest.main()
