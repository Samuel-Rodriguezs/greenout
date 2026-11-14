import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bio_fasta import Registro, formatar, parse

TEXTO = """>seq1 primeira sequência
ACGT
ACGT

>seq2
GGCC
"""


class TestBioFasta(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(
            parse(TEXTO),
            [
                Registro("seq1", "primeira sequência", "ACGTACGT"),
                Registro("seq2", "", "GGCC"),
            ],
        )

    def test_vazio(self):
        self.assertEqual(parse(""), [])
        self.assertEqual(parse("\n\n"), [])

    def test_registro_sem_sequencia(self):
        self.assertEqual(parse(">x"), [Registro("x", "", "")])

    def test_sequencia_sem_cabecalho(self):
        with self.assertRaises(ValueError):
            parse("ACGT\n>x\nAC")

    def test_crlf_e_comentario(self):
        regs = parse(";comentario\r\n>a\r\nAC\r\nGT\r\n")
        self.assertEqual(regs, [Registro("a", "", "ACGT")])

    def test_formatar(self):
        saida = formatar([Registro("s", "d", "ACGTACGTAC")], largura=4)
        self.assertEqual(saida, ">s d\nACGT\nACGT\nAC\n")
        self.assertEqual(formatar([]), "")

    def test_ida_e_volta(self):
        regs = parse(TEXTO)
        self.assertEqual(parse(formatar(regs, 3)), regs)

    def test_largura_invalida(self):
        with self.assertRaises(ValueError):
            formatar([], 0)


if __name__ == "__main__":
    unittest.main()
