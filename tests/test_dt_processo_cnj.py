import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dt_processo_cnj import calcular_dv, formatar_processo, montar_processo, parse_processo, validar_processo


def dv_pela_resolucao(seq: str, ano: str, j: str, tr: str, oooo: str) -> str:
    """Método em três etapas descrito na Resolução CNJ 65/2008 (independente da implementação)."""
    r1 = int(seq) % 97
    r2 = int(f"{r1:02d}{ano}{j}{tr}") % 97
    r3 = int(f"{r2:02d}{oooo}00") % 97
    return f"{98 - r3:02d}"


class TestProcessoCnj(unittest.TestCase):
    def test_valores_conhecidos(self) -> None:
        self.assertEqual(montar_processo(1234567, 2020, 8, 26, 100), "1234567-52.2020.8.26.0100")
        self.assertEqual(montar_processo(1, 2024, 5, 2, 1), "0000001-63.2024.5.02.0001")
        self.assertEqual(montar_processo(0, 2000, 1, 0, 0), "0000000-14.2000.1.00.0000")

    def test_confere_com_metodo_da_resolucao(self) -> None:
        casos = [("1234567", "2020", "8", "26", "0100"), ("0000001", "2024", "5", "02", "0001"),
                 ("9999999", "1999", "4", "03", "9999"), ("0000000", "2000", "1", "00", "0000")]
        for caso in casos:
            with self.subTest(caso=caso):
                self.assertEqual(calcular_dv(*caso), dv_pela_resolucao(*caso))

    def test_validar(self) -> None:
        self.assertTrue(validar_processo("1234567-52.2020.8.26.0100"))
        self.assertTrue(validar_processo("12345675220208260100"))
        self.assertFalse(validar_processo("1234567-53.2020.8.26.0100"))
        self.assertFalse(validar_processo("1234567-52.2020.8.26.0101"))

    def test_formatos_invalidos(self) -> None:
        for n in ("", "123", "1234567-52.2020.8.26.010", "1234567-52.2020.0.26.0100", "abcdefghijklmnopqrst"):
            with self.subTest(n=n):
                self.assertFalse(validar_processo(n))

    def test_parse(self) -> None:
        p = parse_processo("1234567-52.2020.8.26.0100")
        self.assertEqual((p.sequencial, p.dv, p.ano, p.segmento, p.tribunal, p.origem),
                         ("1234567", "52", "2020", 8, "26", "0100"))
        self.assertEqual(p.nome_segmento, "Justiça dos Estados e do DF e Territórios")
        self.assertEqual(str(p), "1234567-52.2020.8.26.0100")

    def test_formatar_sem_mascara(self) -> None:
        self.assertEqual(formatar_processo("12345675220208260100"), "1234567-52.2020.8.26.0100")

    def test_dv_sempre_entre_02_e_98(self) -> None:
        for seq in range(0, 500):
            dv = int(calcular_dv(f"{seq:07d}", "2023", "8", "13", "0024"))
            self.assertTrue(2 <= dv <= 98)

    def test_ida_e_volta(self) -> None:
        for seq in (0, 7, 123456, 9999999):
            for seg in range(1, 10):
                self.assertTrue(validar_processo(montar_processo(seq, 2022, seg, 15, 42)))

    def test_calcular_dv_tamanho_errado(self) -> None:
        with self.assertRaises(ValueError):
            calcular_dv("123", "2020", "8", "26", "0100")


if __name__ == "__main__":
    unittest.main()
