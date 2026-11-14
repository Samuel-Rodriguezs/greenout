import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_alocacao_memoria import Memoria, SemMemoria

LACUNAS = [100, 500, 200, 300, 600]
PEDIDOS = [212, 417, 112, 426]


def cenario() -> Memoria:
    layout = []
    for i, tam in enumerate(LACUNAS):
        layout.append((tam, None))
        if i < len(LACUNAS) - 1:
            layout.append((50, f"SO{i}"))  # separadores ocupados
    return Memoria.de_blocos(layout)


def rodar(estrategia: str) -> dict[str, object]:
    m = cenario()
    saida: dict[str, object] = {}
    for i, tam in enumerate(PEDIDOS):
        try:
            saida[f"p{i}"] = m.alocar(f"p{i}", tam, estrategia)
        except SemMemoria:
            saida[f"p{i}"] = None
    return saida


class TestAlocacaoMemoria(unittest.TestCase):
    def test_first_fit_livro(self):
        # 212 -> lacuna 500 (@150); 417 -> 600 (@1300); 112 -> sobra 288 (@362); 426 não cabe
        self.assertEqual(rodar("first"), {"p0": 150, "p1": 1300, "p2": 362, "p3": None})

    def test_best_fit_livro(self):
        # 212 -> 300 (@950); 417 -> 500 (@150); 112 -> 200 (@700); 426 -> 600 (@1300)
        self.assertEqual(rodar("best"), {"p0": 950, "p1": 150, "p2": 700, "p3": 1300})

    def test_worst_fit_livro(self):
        # 212 -> 600 (@1300); 417 -> 500 (@150); 112 -> sobra 388 (@1512); 426 não cabe
        self.assertEqual(rodar("worst"), {"p0": 1300, "p1": 150, "p2": 1512, "p3": None})

    def test_next_fit_livro(self):
        # 212 -> @150; 417 -> @1300; 112 -> @1717 (continua de onde parou); 426 falha
        self.assertEqual(rodar("next"), {"p0": 150, "p1": 1300, "p2": 1717, "p3": None})

    def test_fragmentacao_externa(self):
        m = cenario()
        m.alocar("p0", 212, "best")
        self.assertEqual(m.livre_total(), 1700 - 212)
        self.assertEqual(m.maior_lacuna(), 600)
        self.assertEqual(m.fragmentacao_externa(), 1488 - 600)

    def test_fragmentacao_interna_com_unidade(self):
        m = Memoria(1000, unidade=64)
        m.alocar("a", 100)  # ocupa 128
        m.alocar("b", 64)  # ocupa 64, sem desperdício
        self.assertEqual(m.fragmentacao_interna(), 28)
        self.assertEqual(m.livre_total(), 1000 - 192)

    def test_liberar_funde_vizinhos(self):
        m = Memoria(300)
        for nome in "abc":
            m.alocar(nome, 100)
        m.liberar("a")
        m.liberar("c")
        self.assertEqual(m.lacunas(), [(0, 100), (200, 100)])
        m.liberar("b")
        self.assertEqual(m.lacunas(), [(0, 300)])

    def test_erros(self):
        m = Memoria(100)
        m.alocar("a", 10)
        with self.assertRaises(ValueError):
            m.alocar("a", 10)
        with self.assertRaises(ValueError):
            m.alocar("b", 10, "random")
        with self.assertRaises(ValueError):
            m.alocar("b", 0)
        with self.assertRaises(KeyError):
            m.liberar("zzz")
        with self.assertRaises(SemMemoria):
            m.alocar("grande", 91)


if __name__ == "__main__":
    unittest.main()
