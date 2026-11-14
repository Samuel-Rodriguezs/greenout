import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_tamanho import ErroTamanho, formatar, parse


class TestFmtTamanho(unittest.TestCase):
    def test_parse_si(self):
        self.assertEqual(parse("1.5GB"), 1_500_000_000)
        self.assertEqual(parse("2 kb"), 2000)
        self.assertEqual(parse("1,5 MB"), 1_500_000)
        self.assertEqual(parse("512"), 512)
        self.assertEqual(parse("100B"), 100)
        self.assertEqual(parse(".5KB"), 500)

    def test_parse_binario(self):
        self.assertEqual(parse("1KiB"), 1024)
        self.assertEqual(parse("1.5 GiB"), 1610612736)
        self.assertEqual(parse("2MiB"), 2 * 1024 * 1024)

    def test_sufixo_sem_b(self):
        self.assertEqual(parse("1k"), 1000)
        self.assertEqual(parse("1k", binario_por_padrao=True), 1024)
        self.assertEqual(parse("1kb", binario_por_padrao=True), 1000)

    def test_formatar(self):
        self.assertEqual(formatar(0), "0 B")
        self.assertEqual(formatar(999), "999 B")
        self.assertEqual(formatar(1500), "1.5 KB")
        self.assertEqual(formatar(1000), "1 KB")
        self.assertEqual(formatar(1536, binario=True), "1.5 KiB")
        self.assertEqual(formatar(999_999), "1 MB")
        self.assertEqual(formatar(3 * 10**12, casas=2), "3 TB")

    def test_ida_e_volta(self):
        for n in (1, 1000, 123456, 10**9):
            self.assertEqual(parse(formatar(n, casas=6).replace(" ", "")), n)

    def test_malformados(self):
        for ruim in ["", "abc", "GB", "1.2.3GB", "-5MB", "1 XB", "1i", "1 ii B", "1KiBB"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroTamanho):
                    parse(ruim)
        with self.assertRaises(ErroTamanho):
            formatar(-1)


if __name__ == "__main__":
    unittest.main()
