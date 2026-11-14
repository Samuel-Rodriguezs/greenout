import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_agregacao import Agrupamento, calcular_agregado
from bd_sql_parser import parse
from bd_volcano import ErroExecucao, Ordenacao, Scan

VENDAS = [("sul", "a", 10), ("sul", "b", 20), ("norte", "a", 5), ("norte", "a", None),
          ("sul", "a", 30), (None, "b", 1)]


def vendas(linhas=VENDAS):
    return Scan("v", ["regiao", "prod", "valor"], linhas)


def agrupar(sql, linhas=VENDAS):
    s = parse(sql)
    saidas = [(i.expr, i.alias or f"c{n}") for n, i in enumerate(s.itens)]
    op = Agrupamento(vendas(linhas), s.group_by, saidas, s.having)
    return sorted(op.todas(), key=repr)


class TestAgregacao(unittest.TestCase):
    def test_funcoes_puras(self):
        self.assertEqual(calcular_agregado("COUNT", [1, None, 2]), 2)
        self.assertEqual(calcular_agregado("COUNT", [1, None, 2], estrela=True), 3)
        self.assertEqual(calcular_agregado("SUM", [1, None, 2]), 3)
        self.assertEqual(calcular_agregado("AVG", [1, None, 2]), 1.5)
        self.assertEqual(calcular_agregado("MIN", ["b", "a"]), "a")
        self.assertEqual(calcular_agregado("MAX", [3, None]), 3)
        self.assertIsNone(calcular_agregado("SUM", [None]))
        self.assertEqual(calcular_agregado("COUNT", []), 0)
        with self.assertRaises(ErroExecucao):
            calcular_agregado("MEDIAN", [1])

    def test_group_by_com_varios_agregados(self):
        r = agrupar("SELECT regiao, COUNT(*), COUNT(valor), SUM(valor), AVG(valor), MIN(valor), MAX(valor) "
                    "FROM v GROUP BY regiao")
        self.assertEqual(r, sorted([("sul", 3, 3, 60, 20.0, 10, 30),
                                    ("norte", 2, 1, 5, 5.0, 5, 5),
                                    (None, 1, 1, 1, 1.0, 1, 1)], key=repr))

    def test_null_forma_seu_proprio_grupo(self):
        r = agrupar("SELECT regiao, COUNT(*) FROM v GROUP BY regiao")
        self.assertIn((None, 1), r)

    def test_agregado_global(self):
        self.assertEqual(agrupar("SELECT COUNT(*), SUM(valor) FROM v"), [(6, 66)])

    def test_global_sobre_entrada_vazia(self):
        self.assertEqual(agrupar("SELECT COUNT(*), SUM(valor), MAX(valor) FROM v", []), [(0, None, None)])

    def test_group_by_sobre_entrada_vazia_nao_gera_linhas(self):
        self.assertEqual(agrupar("SELECT regiao, COUNT(*) FROM v GROUP BY regiao", []), [])

    def test_group_by_multiplas_chaves(self):
        r = agrupar("SELECT regiao, prod, SUM(valor) FROM v GROUP BY regiao, prod")
        self.assertIn(("sul", "a", 40), r)
        self.assertIn(("norte", "a", 5), r)
        self.assertEqual(len(r), 4)

    def test_having(self):
        r = agrupar("SELECT regiao, SUM(valor) FROM v GROUP BY regiao HAVING SUM(valor) > 5 AND COUNT(*) >= 3")
        self.assertEqual(r, [("sul", 60)])

    def test_expressao_sobre_agregado(self):
        r = agrupar("SELECT regiao, SUM(valor) * 2 + 1, UPPER(regiao) FROM v GROUP BY regiao")
        self.assertIn(("sul", 121, "SUL"), r)
        self.assertIn((None, 3, None), r)

    def test_coluna_fora_do_group_by_e_erro(self):
        with self.assertRaises(ErroExecucao):
            agrupar("SELECT regiao, prod, COUNT(*) FROM v GROUP BY regiao")
        with self.assertRaises(ErroExecucao):
            agrupar("SELECT prod, COUNT(*) FROM v")

    def test_agregado_aninhado_e_erro(self):
        with self.assertRaises(ErroExecucao):
            agrupar("SELECT SUM(COUNT(valor)) FROM v")

    def test_sobre_entrada_ordenada_compoe_com_ordenacao(self):
        s = parse("SELECT regiao, SUM(valor) total FROM v GROUP BY regiao")
        agr = Agrupamento(vendas(), s.group_by, [(i.expr, i.alias or "regiao") for i in s.itens])
        o = Ordenacao(agr, [(parse("SELECT regiao FROM t").itens[0].expr, False)])
        self.assertEqual([l[0] for l in o], [None, "norte", "sul"])


if __name__ == "__main__":
    unittest.main()
