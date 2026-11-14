import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from kata_args import ErroArgs, parse


class TestKataArgs(unittest.TestCase):
    def test_sem_argumentos_usa_padroes(self):
        self.assertEqual(parse("l,p#,d*,n##", []),
                         {"l": False, "p": 0, "d": "", "n": 0.0})

    def test_booleano(self):
        self.assertEqual(parse("l", ["-l"]), {"l": True})
        self.assertEqual(parse("l", []), {"l": False})

    def test_inteiro(self):
        self.assertEqual(parse("p#", ["-p", "8080"]), {"p": 8080})
        self.assertEqual(parse("p#", ["-p", "-5"]), {"p": -5})

    def test_string(self):
        self.assertEqual(parse("d*", ["-d", "/usr/logs"]), {"d": "/usr/logs"})

    def test_float(self):
        self.assertEqual(parse("n##", ["-n", "3.14"]), {"n": 3.14})

    def test_exemplo_completo(self):
        r = parse("l,p#,d*", ["-l", "-p", "8080", "-d", "/usr/logs"])
        self.assertEqual(r, {"l": True, "p": 8080, "d": "/usr/logs"})

    def test_ordem_livre(self):
        r = parse("l,p#", ["-p", "1", "-l"])
        self.assertEqual(r, {"l": True, "p": 1})

    def test_valor_ausente(self):
        with self.assertRaises(ErroArgs):
            parse("p#", ["-p"])
        with self.assertRaises(ErroArgs):
            parse("p#,l", ["-p", "-l"])

    def test_valor_invalido(self):
        with self.assertRaises(ErroArgs):
            parse("p#", ["-p", "abc"])
        with self.assertRaises(ErroArgs):
            parse("n##", ["-n", "x"])

    def test_flag_desconhecida_ou_repetida(self):
        with self.assertRaises(ErroArgs):
            parse("l", ["-x"])
        with self.assertRaises(ErroArgs):
            parse("l", ["-l", "-l"])

    def test_argumento_solto(self):
        with self.assertRaises(ErroArgs):
            parse("l", ["foo"])
        with self.assertRaises(ErroArgs):
            parse("l", ["-lx"])

    def test_schema_invalido(self):
        for ruim in ("ab", "1", "p###", "l,l"):
            with self.assertRaises(ErroArgs, msg=ruim):
                parse(ruim, [])

    def test_schema_vazio(self):
        self.assertEqual(parse("", []), {})


if __name__ == "__main__":
    unittest.main()
