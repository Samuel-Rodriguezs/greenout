import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_fastq import (
    Leitura,
    aparar_fim,
    decodificar,
    parse,
    prob_erro,
    qualidade_media,
)

TEXTO = "@r1 desc\nACGT\n+\nI5?!\n@r2\nGG\n+r2\nII\n"


class TestBioFastq(unittest.TestCase):
    def test_decodificar(self):
        self.assertEqual(decodificar("!5?I"), [0, 20, 30, 40])
        self.assertEqual(decodificar("hi", offset=64), [40, 41])
        with self.assertRaises(ValueError):
            decodificar(" ")

    def test_prob_erro(self):
        self.assertAlmostEqual(prob_erro(0), 1.0)
        self.assertAlmostEqual(prob_erro(10), 0.1)
        self.assertAlmostEqual(prob_erro(20), 0.01)

    def test_parse(self):
        self.assertEqual(
            parse(TEXTO), [Leitura("r1", "ACGT", "I5?!"), Leitura("r2", "GG", "II")]
        )

    def test_parse_erros(self):
        with self.assertRaises(ValueError):
            parse("@r\nACGT\n+\n")
        with self.assertRaises(ValueError):
            parse("@r\nACGT\n+\nII\n")
        with self.assertRaises(ValueError):
            parse("r\nAC\n+\nII\n")
        self.assertEqual(parse(""), [])

    def test_media(self):
        self.assertEqual(qualidade_media(Leitura("a", "ACGT", "I5?!")), 22.5)
        with self.assertRaises(ValueError):
            qualidade_media(Leitura("a", "", ""))

    def test_aparar(self):
        self.assertEqual(
            aparar_fim(Leitura("a", "ACGT", "I5?!"), 10), Leitura("a", "ACG", "I5?")
        )
        self.assertEqual(aparar_fim(Leitura("a", "AC", "!!"), 10).sequencia, "")
        self.assertEqual(aparar_fim(Leitura("a", "AC", "II"), 10).sequencia, "AC")


if __name__ == "__main__":
    unittest.main()
