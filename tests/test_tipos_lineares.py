import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_lineares import (BOOL, INT, UNIT, App, Base, ErroLinear, Fn, Lam,
                            Let, LetPar, Lit, Par, Recurso, Se, Tensor,
                            Unidade, Var, e_linear, verificar)

ARQ = Recurso("Arquivo")
PRIM = {
    "abrir": Fn(UNIT, ARQ),
    "ler": Fn(ARQ, Tensor(INT, ARQ)),
    "fechar": Fn(ARQ, UNIT),
}


def v(n):
    return Var(n)


class TestLineares(unittest.TestCase):
    def test_linearidade_dos_tipos(self):
        self.assertFalse(e_linear(INT))
        self.assertTrue(e_linear(ARQ))
        self.assertTrue(e_linear(Tensor(INT, ARQ)))
        self.assertFalse(e_linear(Tensor(INT, BOOL)))
        self.assertTrue(e_linear(Fn(INT, INT, True)))
        self.assertFalse(e_linear(Fn(ARQ, INT)))

    def test_ilimitado_pode_duplicar_e_descartar(self):
        dup = Lam("x", INT, Par(v("x"), v("x")))
        self.assertEqual(verificar(dup), Fn(INT, Tensor(INT, INT)))
        descarta = Lam("x", INT, Lit(0))
        self.assertEqual(verificar(descarta), Fn(INT, INT))

    def test_identidade_linear(self):
        self.assertEqual(verificar(Lam("r", ARQ, v("r"))), Fn(ARQ, ARQ))

    def test_duplicar_recurso_falha(self):
        with self.assertRaisesRegex(ErroLinear, "2 vezes"):
            verificar(Lam("r", ARQ, Par(v("r"), v("r"))))

    def test_descartar_recurso_falha(self):
        with self.assertRaisesRegex(ErroLinear, "não foi consumida"):
            verificar(Lam("r", ARQ, Lit(0)))

    def test_ciclo_de_vida_correto(self):
        # let f = abrir () in let (n, f2) = ler f in let _ = fechar f2 in n
        prog = Let("f", App(v("abrir"), Unidade()),
                   LetPar("n", "g", App(v("ler"), v("f")),
                          Let("u", App(v("fechar"), v("g")), v("n"))))
        self.assertEqual(verificar(prog, PRIM), INT)

    def test_esquecer_de_fechar(self):
        prog = Let("f", App(v("abrir"), Unidade()),
                   LetPar("n", "g", App(v("ler"), v("f")), v("n")))
        with self.assertRaisesRegex(ErroLinear, "g"):
            verificar(prog, PRIM)

    def test_usar_apos_fechar(self):
        prog = Let("f", App(v("abrir"), Unidade()),
                   Let("u", App(v("fechar"), v("f")),
                       App(v("fechar"), v("f"))))
        with self.assertRaisesRegex(ErroLinear, "f"):
            verificar(prog, PRIM)

    def test_recurso_no_contexto_deve_ser_consumido(self):
        ctx = {"r": ARQ, "fechar": PRIM["fechar"]}
        self.assertEqual(verificar(App(v("fechar"), v("r")), ctx), UNIT)
        with self.assertRaises(ErroLinear):
            verificar(Lit(1), ctx)
        with self.assertRaises(ErroLinear):
            verificar(Par(v("r"), v("r")), ctx)

    def test_se_ramos_devem_consumir_igual(self):
        ctx = {"r": ARQ, "fechar": PRIM["fechar"], "c": BOOL}
        ok = Se(v("c"), App(v("fechar"), v("r")), App(v("fechar"), v("r")))
        self.assertEqual(verificar(ok, ctx), UNIT)
        ruim = Se(v("c"), App(v("fechar"), v("r")), Unidade())
        with self.assertRaisesRegex(ErroLinear, "ramos"):
            verificar(ruim, ctx)

    def test_se_com_ilimitado_em_um_ramo_so(self):
        ctx = {"n": INT, "c": BOOL}
        self.assertEqual(verificar(Se(v("c"), v("n"), Lit(0)), ctx), INT)

    def test_condicao_usa_recurso(self):
        ctx = {"b": Recurso("Bit")}
        with self.assertRaises(ErroLinear):  # Recurso nao e Bool
            verificar(Se(v("b"), Lit(1), Lit(2)), ctx)

    def test_fechamento_que_captura_recurso_e_linear(self):
        ctx = {"r": ARQ, "fechar": PRIM["fechar"]}
        f = Lam("u", UNIT, App(v("fechar"), v("r")))
        self.assertEqual(verificar(f, ctx), Fn(UNIT, UNIT, True))

    def test_fechamento_linear_usado_duas_vezes_falha(self):
        ctx = {"r": ARQ, "fechar": PRIM["fechar"]}
        prog = Let("f", Lam("u", UNIT, App(v("fechar"), v("r"))),
                   Par(App(v("f"), Unidade()), App(v("f"), Unidade())))
        with self.assertRaisesRegex(ErroLinear, "f"):
            verificar(prog, ctx)

    def test_fechamento_linear_usado_uma_vez(self):
        ctx = {"r": ARQ, "fechar": PRIM["fechar"]}
        prog = Let("f", Lam("u", UNIT, App(v("fechar"), v("r"))),
                   App(v("f"), Unidade()))
        self.assertEqual(verificar(prog, ctx), UNIT)

    def test_par_com_recurso_exige_consumo_dos_dois(self):
        ok = Lam("p", Tensor(INT, ARQ),
                 LetPar("n", "r", v("p"),
                        Let("u", App(v("fechar"), v("r")), v("n"))))
        self.assertEqual(verificar(ok, {"fechar": PRIM["fechar"]}),
                         Fn(Tensor(INT, ARQ), INT, False))
        ruim = Lam("p", Tensor(INT, ARQ), LetPar("n", "r", v("p"), v("n")))
        with self.assertRaises(ErroLinear):
            verificar(ruim)

    def test_sombreamento_nao_vaza_uso(self):
        # \r:Arquivo. \r:Int. r  -- o r interno é Int; o externo não foi usado
        with self.assertRaises(ErroLinear):
            verificar(Lam("r", ARQ, Lam("r", INT, v("r"))))

    def test_erros_de_tipo_basicos(self):
        with self.assertRaises(ErroLinear):
            verificar(v("x"))
        with self.assertRaises(ErroLinear):
            verificar(App(Lit(1), Lit(2)))
        with self.assertRaises(ErroLinear):
            verificar(App(Lam("x", INT, v("x")), Lit(True)))
        with self.assertRaises(ErroLinear):
            verificar(LetPar("a", "b", Lit(1), Lit(0)))
        with self.assertRaises(ErroLinear):
            verificar(LetPar("a", "a", Par(Lit(1), Lit(2)), Lit(0)))


if __name__ == "__main__":
    unittest.main()
