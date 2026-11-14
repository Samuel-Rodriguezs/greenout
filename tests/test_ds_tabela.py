import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_tabela import Tabela

VENDAS = [
    {"regiao": "N", "produto": "a", "valor": 10},
    {"regiao": "N", "produto": "b", "valor": 20},
    {"regiao": "S", "produto": "a", "valor": 30},
    {"regiao": "S", "produto": "a", "valor": 50},
    {"regiao": "S", "produto": "b", "valor": 5},
]


class TestTabela(unittest.TestCase):
    def setUp(self) -> None:
        self.t = Tabela(VENDAS)

    def test_select_e_filtrar(self):
        s = self.t.filtrar(lambda l: l["valor"] > 15).select("produto", "valor")
        self.assertEqual(s.colunas, ["produto", "valor"])
        self.assertEqual(s.coluna("valor"), [20, 30, 50])
        with self.assertRaises(KeyError):
            self.t.select("x")

    def test_ordenar_multiplas_chaves_e_none(self):
        t = Tabela([{"a": 2, "b": 1}, {"a": None, "b": 0}, {"a": 1, "b": 5}, {"a": 2, "b": 0}])
        self.assertEqual(t.ordenar(["a", "b"]).coluna("b"), [5, 0, 1, 0])
        self.assertEqual(t.ordenar("a", reverso=True).coluna("a"), [2, 2, 1, None])

    def test_agrupar(self):
        g = self.t.agrupar("regiao", {"total": ("valor", "soma"), "media": ("valor", "media"), "n": ("valor", "contagem")})
        self.assertEqual(g.coluna("total"), [30, 85])
        self.assertAlmostEqual(g.coluna("media")[1], 85 / 3)
        self.assertEqual(g.coluna("n"), [2, 3])

    def test_agrupar_callable(self):
        g = self.t.agrupar(["regiao"], {"amp": ("valor", lambda v: max(v) - min(v))})
        self.assertEqual(g.coluna("amp"), [10, 45])

    def test_join_inner_e_left(self):
        nomes = Tabela([{"regiao": "N", "nome": "Norte"}, {"regiao": "X", "nome": "Xis"}])
        i = self.t.join(nomes, "regiao")
        self.assertEqual(len(i), 2)
        self.assertEqual(i.coluna("nome"), ["Norte", "Norte"])
        l = self.t.join(nomes, "regiao", how="left")
        self.assertEqual(len(l), 5)
        self.assertEqual(l.coluna("nome")[2], None)

    def test_join_colisao_de_nomes(self):
        outra = Tabela([{"regiao": "N", "valor": 99}])
        j = self.t.join(outra, "regiao")
        self.assertIn("valor_dir", j.colunas)
        self.assertEqual(j.coluna("valor_dir"), [99, 99])

    def test_pivot(self):
        p = self.t.pivot("regiao", "produto", "valor")
        self.assertEqual(p.colunas, ["regiao", "a", "b"])
        self.assertEqual(p.linhas(), [{"regiao": "N", "a": 10, "b": 20}, {"regiao": "S", "a": 80, "b": 5}])

    def test_pivot_celula_vazia(self):
        t = Tabela([{"i": 1, "c": "x", "v": 3}, {"i": 2, "c": "y", "v": 4}])
        self.assertEqual(t.pivot("i", "c", "v").linhas(), [{"i": 1, "x": 3, "y": None}, {"i": 2, "x": None, "y": 4}])

    def test_adicionar_coluna_e_head(self):
        t = self.t.adicionar_coluna("dobro", lambda l: l["valor"] * 2)
        self.assertEqual(t.head(2).coluna("dobro"), [20, 40])

    def test_agregacao_invalida(self):
        with self.assertRaises(ValueError):
            self.t.agrupar("regiao", {"x": ("valor", "inexistente")})


if __name__ == "__main__":
    unittest.main()
