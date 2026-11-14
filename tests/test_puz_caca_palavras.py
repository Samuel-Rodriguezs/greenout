import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_caca_palavras import DIRECOES, formatar, gerar, procurar, resolver

PALAVRAS = ["python", "teste", "busca", "grade", "ciclo"]


class TestCacaPalavras(unittest.TestCase):
    def test_gerar_posiciona_todas(self):
        grade, pos = gerar(PALAVRAS, 10, 10, seed=4)
        self.assertEqual(len(grade), 10)
        self.assertEqual(set(pos), {p.upper() for p in PALAVRAS})
        for p, (r, c, d) in pos.items():
            dr, dc = DIRECOES[d]
            lido = "".join(grade[r + i * dr][c + i * dc] for i in range(len(p)))
            self.assertEqual(lido, p)

    def test_determinismo_por_seed(self):
        self.assertEqual(gerar(PALAVRAS, 9, 9, 7), gerar(PALAVRAS, 9, 9, 7))
        self.assertNotEqual(gerar(PALAVRAS, 9, 9, 7)[0], gerar(PALAVRAS, 9, 9, 8)[0])

    def test_solver_encontra_as_geradas(self):
        grade, _ = gerar(PALAVRAS, 10, 10, seed=11)
        achadas = resolver(grade, PALAVRAS)
        self.assertTrue(all(v is not None for v in achadas.values()))

    def test_procurar_manual_todas_as_direcoes(self):
        grade = [list("ABC"), list("DEF"), list("GHI")]
        esperado = {"ABC": (0, 0, "E"), "CBA": (0, 2, "O"), "ADG": (0, 0, "S"),
                    "GDA": (2, 0, "N"), "AEI": (0, 0, "SE"), "IEA": (2, 2, "NO"),
                    "CEG": (0, 2, "SO"), "GEC": (2, 0, "NE")}
        for palavra, pos in esperado.items():
            self.assertEqual(procurar(grade, palavra), [pos], palavra)

    def test_diagonais(self):
        grade = [list("AXX"), list("XBX"), list("XXC")]
        self.assertEqual(procurar(grade, "abc"), [(0, 0, "SE")])
        self.assertEqual(procurar(grade, "cba"), [(2, 2, "NO")])

    def test_palavra_ausente(self):
        grade, _ = gerar(["sol"], 4, 4, seed=1)
        self.assertEqual(procurar(grade, "zzzzzz"), [])
        self.assertIsNone(resolver(grade, ["zzzzzz"])["ZZZZZZ"])
        self.assertEqual(procurar(grade, ""), [])

    def test_nao_cabe(self):
        with self.assertRaises(ValueError):
            gerar(["abcdefgh"], 3, 3, seed=1)

    def test_palavra_invalida(self):
        with self.assertRaises(ValueError):
            gerar(["a1"], 3, 3, seed=1)

    def test_sobreposicao_compativel(self):
        # direções restritas forçam cruzamentos; ainda assim a leitura deve ser consistente
        grade, pos = gerar(["abc", "cde"], 3, 3, seed=2, direcoes=["E", "S"])
        for p, (r, c, d) in pos.items():
            dr, dc = DIRECOES[d]
            self.assertEqual("".join(grade[r + i * dr][c + i * dc] for i in range(3)), p)

    def test_formatar(self):
        self.assertEqual(formatar([["A", "B"], ["C", "D"]]), "A B\nC D")


if __name__ == "__main__":
    unittest.main()
