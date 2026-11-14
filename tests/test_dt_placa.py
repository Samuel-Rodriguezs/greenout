import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_placa import (
    antiga_para_mercosul,
    formatar_placa,
    mercosul_para_antiga,
    normalizar_placa,
    tipo_placa,
    validar_placa,
)


class TestPlaca(unittest.TestCase):
    def test_tipos(self) -> None:
        self.assertEqual(tipo_placa("ABC-1234"), "antiga")
        self.assertEqual(tipo_placa("abc1234"), "antiga")
        self.assertEqual(tipo_placa("ABC1D23"), "mercosul")
        self.assertEqual(tipo_placa("abc-1d23"), "mercosul")

    def test_invalidas(self) -> None:
        for p in ("", "AB-1234", "ABCD123", "ABC12345", "1BC1D23", "ABC1DD3", "ABC-12D4", "ÁBC1234"):
            with self.subTest(p=p):
                self.assertFalse(validar_placa(p))
                self.assertIsNone(tipo_placa(p))

    def test_conversao(self) -> None:
        self.assertEqual(antiga_para_mercosul("ABC-1234"), "ABC1C34")
        self.assertEqual(antiga_para_mercosul("XYZ0000"), "XYZ0A00")
        self.assertEqual(antiga_para_mercosul("XYZ9959"), "XYZ9J59")
        self.assertEqual(mercosul_para_antiga("ABC1C34"), "ABC1234")

    def test_conversao_ida_e_volta(self) -> None:
        for digito in range(10):
            antiga = f"QWE1{digito}99"
            self.assertEqual(mercosul_para_antiga(antiga_para_mercosul(antiga)), antiga)

    def test_conversao_invalida(self) -> None:
        with self.assertRaises(ValueError):
            antiga_para_mercosul("ABC1D23")
        with self.assertRaises(ValueError):
            mercosul_para_antiga("ABC1234")
        with self.assertRaises(ValueError):
            mercosul_para_antiga("ABC1K23")

    def test_formatar(self) -> None:
        self.assertEqual(formatar_placa("abc1234"), "ABC-1234")
        self.assertEqual(formatar_placa("abc-1d23"), "ABC1D23")
        self.assertEqual(normalizar_placa(" abc-1234 "), "ABC1234")
        with self.assertRaises(ValueError):
            formatar_placa("xx")


if __name__ == "__main__":
    unittest.main()
