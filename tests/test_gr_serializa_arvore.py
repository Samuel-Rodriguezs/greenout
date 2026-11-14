import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from gr_serializa_arvore import No, desserializar, serializar


class TestSerializa(unittest.TestCase):
    def test_exemplo(self):
        r = No(1, No(2), No(3, No(4), None))
        self.assertEqual(serializar(r), "1,2,#,#,3,4,#,#,#")

    def test_ida_e_volta(self):
        r = No(1, No(-2, None, No(5)), No(3, No(4), No(0)))
        self.assertEqual(desserializar(serializar(r)), r)

    def test_vazia(self):
        self.assertEqual(serializar(None), "#")
        self.assertIsNone(desserializar("#"))

    def test_no_unico(self):
        self.assertEqual(desserializar("7,#,#"), No(7))

    def test_cadeia_profunda(self):
        raiz = No(0)
        atual = raiz
        for i in range(1, 5000):
            atual.dir = No(i)
            atual = atual.dir
        texto = serializar(raiz)
        folha = desserializar(texto)
        self.assertEqual(serializar(folha), texto)

    def test_invalidos(self):
        for ruim in ("", "1,2", "1,#,#,#", "x,#,#"):
            with self.assertRaises(ValueError, msg=ruim):
                desserializar(ruim)


if __name__ == "__main__":
    unittest.main()
