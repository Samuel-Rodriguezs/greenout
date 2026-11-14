import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_slab import CacheSlab, SemMemoria


class TestSlab(unittest.TestCase):
    def test_geometria(self):
        c = CacheSlab(100, 4096)
        self.assertEqual(c.por_slab, 40)
        self.assertEqual(c.desperdicio_por_slab, 96)

    def test_cria_slab_quando_cheio(self):
        c = CacheSlab(1024, 4096)  # 4 objetos por slab
        hs = [c.alocar() for _ in range(5)]
        self.assertEqual(hs[:4], [(0, 0), (0, 1), (0, 2), (0, 3)])
        self.assertEqual(hs[4], (1, 0))
        self.assertEqual(c.contagem(), {"cheio": 1, "parcial": 1, "vazio": 0})
        self.assertEqual(c.bytes_reservados(), 8192)

    def test_prefere_parcial_e_reusa_posicao(self):
        c = CacheSlab(1024, 4096)
        hs = [c.alocar() for _ in range(5)]
        c.liberar(hs[1])  # slab 0 vira parcial, posição 1 livre
        self.assertEqual(c.alocar(), (0, 1))
        self.assertEqual(c.contagem()["cheio"], 1)
        self.assertEqual(len(c.slabs), 2)

    def test_encolher_devolve_so_vazios(self):
        c = CacheSlab(2048, 4096)  # 2 por slab
        hs = [c.alocar() for _ in range(4)]
        c.liberar(hs[0])
        c.liberar(hs[1])
        self.assertEqual(c.contagem(), {"cheio": 1, "parcial": 0, "vazio": 1})
        self.assertEqual(c.encolher(), 1)
        self.assertEqual(c.bytes_reservados(), 4096)
        self.assertEqual(c.objetos_em_uso(), 2)

    def test_slab_vazio_e_reaproveitado_antes_de_criar_outro(self):
        c = CacheSlab(2048, 4096)
        a, b = c.alocar(), c.alocar()
        c.liberar(a)
        c.liberar(b)
        self.assertEqual(c.alocar(), (0, 0))
        self.assertEqual(len(c.slabs), 1)

    def test_limite_de_slabs(self):
        c = CacheSlab(2048, 4096, max_slabs=1)
        c.alocar()
        c.alocar()
        with self.assertRaises(SemMemoria):
            c.alocar()

    def test_liberacao_invalida(self):
        c = CacheSlab(1024, 4096)
        h = c.alocar()
        c.liberar(h)
        with self.assertRaises(KeyError):
            c.liberar(h)  # dupla
        with self.assertRaises(KeyError):
            c.liberar((9, 0))
        with self.assertRaises(KeyError):
            c.liberar((0, 99))

    def test_objeto_maior_que_slab(self):
        with self.assertRaises(ValueError):
            CacheSlab(5000, 4096)


if __name__ == "__main__":
    unittest.main()
