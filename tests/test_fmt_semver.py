import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_semver import ErroSemver, Versao, comparar, maior_satisfatoria, parse, satisfaz


class TestFmtSemver(unittest.TestCase):
    def test_parse(self):
        v = parse("v1.2.3-alpha.1+build.5")
        self.assertEqual((v.maior, v.menor, v.patch, v.pre, v.build), (1, 2, 3, ("alpha", "1"), ("build", "5")))
        self.assertEqual(str(v), "1.2.3-alpha.1+build.5")

    def test_ordem_da_especificacao(self):
        ordem = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2",
                 "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
        vs = [parse(x) for x in ordem]
        self.assertEqual(sorted(reversed(vs)), vs)

    def test_comparar_ignora_build(self):
        self.assertEqual(comparar("1.0.0+a", "1.0.0+b"), 0)
        self.assertEqual(comparar("1.10.0", "1.9.0"), 1)
        self.assertEqual(comparar("0.0.1", "0.1.0"), -1)

    def test_incrementar(self):
        self.assertEqual(str(parse("1.2.3").incrementar("menor")), "1.3.0")
        self.assertEqual(str(parse("1.2.3").incrementar("maior")), "2.0.0")
        with self.assertRaises(ErroSemver):
            parse("1.2.3").incrementar("x")

    def test_intervalos(self):
        casos = [
            ("1.2.3", "^1.2.0", True), ("2.0.0", "^1.2.0", False), ("1.1.9", "^1.2.0", False),
            ("0.2.5", "^0.2.3", True), ("0.3.0", "^0.2.3", False), ("0.0.4", "^0.0.3", False),
            ("1.2.9", "~1.2.3", True), ("1.3.0", "~1.2.3", False),
            ("1.5.0", ">=1.2.0 <2.0.0", True), ("2.0.0", ">=1.2.0 <2.0.0", False),
            ("1.2.7", "1.2.x", True), ("1.3.0", "1.2.x", False), ("9.9.9", "*", True),
            ("1.5.0", "1.0.0 - 2.0.0", True), ("2.1.0", "1.0.0 - 2.0.0", False),
            ("3.0.0", "^1.0.0 || ^3.0.0", True), ("2.0.0", "^1.0.0 || ^3.0.0", False),
            ("1.2.3", "1.2.3", True), ("1.2.4", "=1.2.3", False), ("1.2.4", ">= 1.2.3", True),
            ("1.2.3-beta", "^1.0.0", False), ("1.2.3-beta", ">=1.2.3-alpha", True),
        ]
        for v, r, esperado in casos:
            with self.subTest(v=v, r=r):
                self.assertEqual(satisfaz(v, r), esperado)

    def test_maior_satisfatoria(self):
        self.assertEqual(maior_satisfatoria(["1.0.0", "1.4.2", "1.10.0", "2.0.0"], "^1.0.0"), "1.10.0")
        self.assertIsNone(maior_satisfatoria(["1.0.0"], "^2.0.0"))

    def test_malformadas(self):
        for ruim in ["", "1", "1.2", "01.2.3", "1.2.3-", "1.2.3-01", "a.b.c", "1.2.3.4", "1.2.3+"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroSemver):
                    parse(ruim)
        with self.assertRaises(ErroSemver):
            satisfaz("1.0.0", "^abc")
        with self.assertRaises(ErroSemver):
            satisfaz("x", "*")

    def test_hash_e_igualdade(self):
        self.assertEqual(len({parse("1.0.0+a"), parse("1.0.0+b")}), 1)
        self.assertIsInstance(parse("1.0.0"), Versao)


if __name__ == "__main__":
    unittest.main()
