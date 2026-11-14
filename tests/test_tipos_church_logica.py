import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_church import de_int, para_int
from tipos_church_logica import (E, FALSO, NAO, OU, SE, VERDADEIRO, XOU,
                                 aplicar, de_bool, igual_a, par, para_bool,
                                 primeiro, segundo)
from tipos_termos import analisar


class TestLogica(unittest.TestCase):
    def test_constantes(self):
        self.assertTrue(para_bool(VERDADEIRO))
        self.assertFalse(para_bool(FALSO))

    def test_nao(self):
        for b in (True, False):
            self.assertEqual(para_bool(aplicar(NAO, de_bool(b))), not b)

    def test_tabelas_verdade(self):
        for a, b in itertools.product((True, False), repeat=2):
            ta, tb = de_bool(a), de_bool(b)
            self.assertEqual(para_bool(aplicar(E, ta, tb)), a and b)
            self.assertEqual(para_bool(aplicar(OU, ta, tb)), a or b)
            self.assertEqual(para_bool(aplicar(XOU, ta, tb)), a != b)

    def test_se(self):
        x, y = analisar("x"), analisar("y")
        self.assertEqual(igual_a(aplicar(SE, VERDADEIRO, x, y), x), True)
        self.assertEqual(igual_a(aplicar(SE, FALSO, x, y), y), True)

    def test_se_e_preguicoso_em_ordem_normal(self):
        omega = analisar("(\\x.x x) (\\x.x x)")
        self.assertTrue(igual_a(aplicar(SE, VERDADEIRO, analisar("ok"), omega),
                                analisar("ok")))

    def test_pares(self):
        p = par(de_int(3), de_int(7))
        self.assertEqual(para_int(primeiro(p)), 3)
        self.assertEqual(para_int(segundo(p)), 7)

    def test_par_aninhado(self):
        p = par(par(analisar("a"), analisar("b")), analisar("c"))
        self.assertTrue(igual_a(segundo(primeiro(p)), analisar("b")))
        self.assertTrue(igual_a(segundo(p), analisar("c")))

    def test_nao_booleano(self):
        with self.assertRaises(ValueError):
            para_bool(analisar("\\t f.z"))


if __name__ == "__main__":
    unittest.main()
