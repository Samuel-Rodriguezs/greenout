import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_dotenv import ErroDotenv, parse, serializar


class TestFmtDotenv(unittest.TestCase):
    def test_basico(self):
        txt = "# comentário\nA=1\nexport B = dois  # inline\n\nC=\nD='$A literal'\n"
        self.assertEqual(parse(txt, ambiente={}), {"A": "1", "B": "dois", "C": "", "D": "$A literal"})

    def test_aspas_duplas_e_escapes(self):
        self.assertEqual(parse('X="a\\nb \\"q\\" # não é comentário" # sim', ambiente={}),
                         {"X": 'a\nb "q" # não é comentário'})

    def test_multilinha(self):
        self.assertEqual(parse('K="linha1\nlinha2"\nZ=1', ambiente={}), {"K": "linha1\nlinha2", "Z": "1"})

    def test_interpolacao(self):
        r = parse("HOST=db\nURL=postgres://${HOST}:5432/$HOST\nP=${PORTA:-80}\nE=${DO_AMB}", ambiente={"DO_AMB": "x"})
        self.assertEqual(r["URL"], "postgres://db:5432/db")
        self.assertEqual((r["P"], r["E"]), ("80", "x"))
        self.assertEqual(parse("A=1\nB=$A", interpolar=False, ambiente={})["B"], "$A")

    def test_dolar_escapado(self):
        self.assertEqual(parse('A="preco \\$5"', ambiente={}), {"A": "preco $5"})

    def test_ida_e_volta(self):
        d = {"A": "simples", "B": 'com "aspas" e $x', "C": "multi\nlinha", "D": ""}
        self.assertEqual(parse(serializar(d), ambiente={}), d)

    def test_malformados(self):
        for ruim in ["SEM_IGUAL", "1A=x", "A B=c", 'A="aberta', "A='aberta", 'A="x" lixo', "=v"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroDotenv):
                    parse(ruim, ambiente={})
        with self.assertRaises(ErroDotenv):
            serializar({"1x": "y"})


if __name__ == "__main__":
    unittest.main()
