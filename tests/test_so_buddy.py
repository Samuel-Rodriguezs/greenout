import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_buddy import Buddy, SemMemoria


class TestBuddy(unittest.TestCase):
    def test_divisoes_sucessivas(self):
        b = Buddy(1024, 64)
        self.assertEqual(b.alocar(100), 0)  # 128 @0
        self.assertEqual(b.blocos_livres(), [(128, 128), (256, 256), (512, 512)])
        self.assertEqual(b.alocar(240), 256)  # 256 @256
        self.assertEqual(b.alocar(64), 128)  # divide 128 @128
        self.assertEqual(b.blocos_livres(), [(192, 64), (512, 512)])
        self.assertEqual(b.alocar(256), 512)
        self.assertEqual(b.blocos_livres(), [(192, 64), (768, 256)])

    def test_fusao_completa_restaura_memoria(self):
        b = Buddy(1024, 64)
        a = b.alocar(100)
        bb = b.alocar(240)
        c = b.alocar(64)
        d = b.alocar(256)
        b.liberar(a)  # companheiro (@128) está dividido: sem fusão
        self.assertIn((0, 128), b.blocos_livres())
        b.liberar(c)  # funde 64+64 -> 128, depois 128+128 -> 256 @0
        self.assertEqual(b.blocos_livres(), [(0, 256), (768, 256)])
        b.liberar(bb)  # 256@0 + 256@256 -> 512@0
        self.assertEqual(b.blocos_livres(), [(0, 512), (768, 256)])
        b.liberar(d)
        self.assertEqual(b.blocos_livres(), [(0, 1024)])

    def test_fragmentacao_interna(self):
        b = Buddy(1024, 64)
        b.alocar(100)  # 128 -> 28 de desperdício
        b.alocar(240)  # 256 -> 16
        b.alocar(65)  # 128 -> 63
        self.assertEqual(b.fragmentacao_interna(), 28 + 16 + 63)
        self.assertEqual(b.livre_total(), 1024 - 128 - 256 - 128)

    def test_esgotamento(self):
        b = Buddy(256, 64)
        enderecos = [b.alocar(64) for _ in range(4)]
        self.assertEqual(enderecos, [0, 64, 128, 192])
        with self.assertRaises(SemMemoria):
            b.alocar(1)
        b.liberar(0)
        b.liberar(128)  # não são companheiros: sem fusão
        with self.assertRaises(SemMemoria):
            b.alocar(128)
        b.liberar(64)  # funde 0+64 -> 128@0
        self.assertEqual(b.alocar(128), 0)

    def test_pedido_maior_que_total(self):
        with self.assertRaises(SemMemoria):
            Buddy(128).alocar(129)

    def test_validacao(self):
        with self.assertRaises(ValueError):
            Buddy(100)
        with self.assertRaises(ValueError):
            Buddy(64, 128)
        b = Buddy(64)
        with self.assertRaises(ValueError):
            b.alocar(0)
        with self.assertRaises(KeyError):
            b.liberar(8)


if __name__ == "__main__":
    unittest.main()
