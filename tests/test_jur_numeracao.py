import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_numeracao import Numerador, interpretar


class TestNumeracao(unittest.TestCase):
    def test_sequencia_por_tipo_e_ano(self):
        n = Numerador()
        self.assertEqual(n.proximo("PET", 2024), "PET-2024/0001")
        self.assertEqual(n.proximo("PET", 2024), "PET-2024/0002")
        self.assertEqual(n.proximo("CON", 2024), "CON-2024/0001")
        self.assertEqual(n.proximo("PET", 2025), "PET-2025/0001")

    def test_invalidos(self):
        n = Numerador()
        with self.assertRaises(ValueError):
            n.proximo("XXX", 2024)
        with self.assertRaises(ValueError):
            n.proximo("PET", 24)

    def test_registrar_existente(self):
        n = Numerador()
        n.registrar_existente("PET-2024/0010")
        n.registrar_existente("PET-2024/0003")  # não regride
        self.assertEqual(n.proximo("PET", 2024), "PET-2024/0011")
        with self.assertRaises(ValueError):
            n.registrar_existente("ZZZ-2024/0001")

    def test_interpretar(self):
        self.assertEqual(interpretar("REC-2023/0042"), ("REC", 2023, 42))
        for ruim in ("rec-2023/1", "REC-2023-0001", "REC2023/0001"):
            with self.assertRaises(ValueError):
                interpretar(ruim)

    def test_lacunas(self):
        n = Numerador()
        self.assertEqual(n.lacunas("PET", 2024, [1, 2, 5, 7]), [3, 4, 6])
        self.assertEqual(n.lacunas("PET", 2024, []), [])
        self.assertEqual(n.ultimo("PET", 2024), 0)

    def test_tipos_customizados(self):
        n = Numerador({"MEM": "memorial"})
        self.assertEqual(n.proximo("MEM", 2024), "MEM-2024/0001")
        with self.assertRaises(ValueError):
            n.proximo("PET", 2024)


if __name__ == "__main__":
    unittest.main()
