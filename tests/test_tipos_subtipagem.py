import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_subtipagem import (Base, Bot, Fn, Hierarquia, Lst, Top, intersectar,
                              juntar, reg, subtipo, valor_tem_tipo)

NAT, INT, NUM, FLOAT, STR = (Base(n) for n in ("Nat", "Int", "Num", "Float", "Str"))


class TestSubtipagem(unittest.TestCase):
    def test_top_bot(self):
        for t in (NAT, reg(x=INT), Fn(INT, INT), Lst(NAT)):
            self.assertTrue(subtipo(t, Top()))
            self.assertTrue(subtipo(Bot(), t))
            self.assertFalse(subtipo(Top(), t))
            self.assertFalse(subtipo(t, Bot()))

    def test_reflexiva_e_transitiva_em_base(self):
        self.assertTrue(subtipo(NAT, NAT))
        self.assertTrue(subtipo(NAT, NUM))
        self.assertFalse(subtipo(NUM, NAT))
        self.assertFalse(subtipo(FLOAT, INT))

    def test_registro_largura(self):
        ponto3 = reg(x=INT, y=INT, z=INT)
        ponto2 = reg(x=INT, y=INT)
        self.assertTrue(subtipo(ponto3, ponto2))
        self.assertFalse(subtipo(ponto2, ponto3))

    def test_registro_profundidade(self):
        self.assertTrue(subtipo(reg(x=NAT), reg(x=NUM)))
        self.assertFalse(subtipo(reg(x=NUM), reg(x=NAT)))

    def test_registro_ordem_irrelevante(self):
        a = reg(a=INT, b=STR)
        b = reg(b=STR, a=INT)
        self.assertEqual(a, b)

    def test_registro_vazio_e_topo_dos_registros(self):
        self.assertTrue(subtipo(reg(x=INT), reg()))
        self.assertFalse(subtipo(reg(), reg(x=INT)))

    def test_registro_aninhado(self):
        a = reg(p=reg(x=NAT, y=INT), nome=STR)
        b = reg(p=reg(x=INT))
        self.assertTrue(subtipo(a, b))

    def test_funcao_contra_e_covariante(self):
        self.assertTrue(subtipo(Fn(NUM, NAT), Fn(INT, NUM)))
        self.assertFalse(subtipo(Fn(NAT, NAT), Fn(INT, NAT)))   # arg estreito demais
        self.assertFalse(subtipo(Fn(NUM, NUM), Fn(NUM, NAT)))   # resultado largo demais

    def test_funcao_de_ordem_superior(self):
        # (A->B)->C  <:  (A'->B')->C' quando A'->B' <: A->B e C <: C'
        f = Fn(Fn(INT, NUM), INT)
        g = Fn(Fn(NUM, NAT), NUM)
        self.assertTrue(subtipo(f, g))
        self.assertFalse(subtipo(g, f))

    def test_funcao_com_registros(self):
        usa_x = Fn(reg(x=INT), INT)
        usa_xy = Fn(reg(x=INT, y=INT), INT)
        # quem aceita qualquer {x} serve onde se passa {x,y}
        self.assertTrue(subtipo(usa_x, usa_xy))
        self.assertFalse(subtipo(usa_xy, usa_x))

    def test_lista_covariante(self):
        self.assertTrue(subtipo(Lst(NAT), Lst(NUM)))
        self.assertFalse(subtipo(Lst(NUM), Lst(NAT)))

    def test_formas_diferentes(self):
        self.assertFalse(subtipo(NAT, Fn(NAT, NAT)))
        self.assertFalse(subtipo(reg(), Lst(NAT)))

    def test_juncao(self):
        self.assertEqual(juntar(NAT, FLOAT), NUM)
        self.assertEqual(juntar(NAT, INT), INT)
        self.assertEqual(juntar(NAT, STR), Top())
        self.assertEqual(juntar(reg(x=NAT, y=INT), reg(x=FLOAT, z=STR)), reg(x=NUM))
        self.assertEqual(juntar(Lst(NAT), Lst(FLOAT)), Lst(NUM))

    def test_juncao_funcoes(self):
        r = juntar(Fn(INT, NAT), Fn(NAT, FLOAT))
        self.assertEqual(r, Fn(NAT, NUM))
        self.assertTrue(subtipo(Fn(INT, NAT), r))
        self.assertTrue(subtipo(Fn(NAT, FLOAT), r))

    def test_intersecao(self):
        self.assertEqual(intersectar(NAT, INT), NAT)
        self.assertEqual(intersectar(NAT, STR), Bot())
        self.assertEqual(intersectar(reg(x=INT), reg(y=STR)), reg(x=INT, y=STR))
        self.assertEqual(intersectar(reg(x=NAT), reg(x=STR)), Bot())
        self.assertEqual(intersectar(Fn(NAT, NUM), Fn(FLOAT, INT)), Fn(NUM, INT))

    def test_juncao_e_cota_superior(self):
        pares = [(reg(x=NAT, y=INT), reg(x=INT, z=INT)), (Fn(NAT, NAT), Fn(INT, INT))]
        for a, b in pares:
            j = juntar(a, b)
            self.assertTrue(subtipo(a, j) and subtipo(b, j))
            m = intersectar(a, b)
            self.assertTrue(subtipo(m, a) and subtipo(m, b))

    def test_hierarquia_ciclo(self):
        h = Hierarquia([("A", "B")])
        with self.assertRaises(ValueError):
            h.declarar("B", "A")

    def test_hierarquia_sem_uniao_unica(self):
        h = Hierarquia([("A", "X"), ("A", "Y"), ("B", "X"), ("B", "Y")])
        self.assertIsNone(h.uniao("A", "B"))
        self.assertEqual(juntar(Base("A"), Base("B"), h), Top())

    def test_valor_em_tempo_de_execucao(self):
        self.assertTrue(valor_tem_tipo(3, NAT))
        self.assertTrue(valor_tem_tipo(-3, INT))
        self.assertFalse(valor_tem_tipo(-3, NAT))
        self.assertFalse(valor_tem_tipo(True, INT))
        self.assertTrue(valor_tem_tipo(2.5, NUM))
        self.assertTrue(valor_tem_tipo({"x": 1, "y": "a", "extra": 0}, reg(x=INT, y=STR)))
        self.assertFalse(valor_tem_tipo({"x": 1}, reg(x=INT, y=STR)))
        self.assertTrue(valor_tem_tipo([1, 2], Lst(NAT)))
        self.assertFalse(valor_tem_tipo([1, -2], Lst(NAT)))
        self.assertTrue(valor_tem_tipo(len, Fn(STR, INT)))
        self.assertFalse(valor_tem_tipo(1, Bot()))


if __name__ == "__main__":
    unittest.main()
