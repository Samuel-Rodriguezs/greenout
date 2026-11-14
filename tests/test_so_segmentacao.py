import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_segmentacao import FaltaDeSegmentacao, Segmentacao, SemMemoria


def livro() -> Segmentacao:
    s = Segmentacao(8000)
    s.registrar(0, 1400, 1000)
    s.registrar(1, 6300, 400, "r")
    s.registrar(2, 4300, 400)
    s.registrar(3, 3200, 1100, "rx")
    s.registrar(4, 4700, 1000)
    return s


class TestSegmentacao(unittest.TestCase):
    def test_exemplos_silberschatz(self):
        s = livro()
        self.assertEqual(s.traduzir(2, 53), 4353)
        self.assertEqual(s.traduzir(3, 852, "x"), 4052)
        with self.assertRaises(FaltaDeSegmentacao):
            s.traduzir(0, 1222)  # limite é 1000

    def test_limite_exato(self):
        s = livro()
        self.assertEqual(s.traduzir(1, 399), 6699)
        with self.assertRaises(FaltaDeSegmentacao):
            s.traduzir(1, 400)
        with self.assertRaises(FaltaDeSegmentacao):
            s.traduzir(1, -1)

    def test_protecao_e_inexistente(self):
        s = livro()
        with self.assertRaises(FaltaDeSegmentacao):
            s.traduzir(1, 0, "w")  # somente leitura
        with self.assertRaises(FaltaDeSegmentacao):
            s.traduzir(9, 0)

    def test_lacunas_do_exemplo(self):
        self.assertEqual(
            livro().lacunas(),
            [(0, 1400), (2400, 800), (5700, 600), (6700, 1300)],
        )

    def test_sobreposicao_e_limites(self):
        s = livro()
        with self.assertRaises(ValueError):
            s.registrar(5, 1000, 500)  # invade o segmento 0
        with self.assertRaises(ValueError):
            s.registrar(5, 7900, 500)  # passa do fim da memória
        with self.assertRaises(ValueError):
            s.registrar(0, 0, 10)  # duplicado
        with self.assertRaises(ValueError):
            s.registrar(5, 0, 10, "z")

    def test_fragmentacao_externa_e_compactacao(self):
        s = Segmentacao(1000)
        s.alocar(0, 300)
        s.alocar(1, 200)
        s.alocar(2, 300)
        s.liberar(1)
        self.assertEqual(s.livre_total(), 400)
        self.assertEqual(s.maior_lacuna(), 200)
        with self.assertRaises(SemMemoria):
            s.alocar(3, 350)
        self.assertEqual(s.compactar(), 1)  # só o segmento 2 se move
        self.assertEqual(s.tabela[2].base, 300)
        self.assertEqual(s.maior_lacuna(), 400)
        self.assertEqual(s.alocar(3, 350), 600)

    def test_first_fit_reaproveita_buraco(self):
        s = Segmentacao(100)
        s.alocar(0, 30)
        s.alocar(1, 30)
        s.liberar(0)
        self.assertEqual(s.alocar(2, 20), 0)


if __name__ == "__main__":
    unittest.main()
