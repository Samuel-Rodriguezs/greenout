import csv
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_csv import ErroCSV, analisar, analisar_dicts, gerar


class TestCSV(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(analisar("a,b,c\n1,2,3"), [["a", "b", "c"], ["1", "2", "3"]])

    def test_aspas_com_virgula_e_quebra(self):
        txt = 'nome,obs\n"Silva, Ana","linha1\nlinha2"\n'
        self.assertEqual(analisar(txt), [["nome", "obs"], ["Silva, Ana", "linha1\nlinha2"]])

    def test_aspas_escapadas(self):
        self.assertEqual(analisar('"ele disse ""oi"""'), [['ele disse "oi"']])

    def test_campos_vazios(self):
        self.assertEqual(analisar("a,,c\n,\n"), [["a", "", "c"], ["", ""]])

    def test_crlf(self):
        self.assertEqual(analisar("a,b\r\nc,d\r\n"), [["a", "b"], ["c", "d"]])

    def test_separador_ponto_e_virgula(self):
        self.assertEqual(analisar("a;b,c", ";"), [["a", "b,c"]])

    def test_dicts(self):
        self.assertEqual(analisar_dicts("x,y\n1,2\n3,4\n"), [{"x": "1", "y": "2"}, {"x": "3", "y": "4"}])
        self.assertEqual(analisar_dicts(""), [])

    def test_dicts_colunas_erradas(self):
        with self.assertRaises(ErroCSV):
            analisar_dicts("x,y\n1\n")

    def test_erros(self):
        for txt in ['"abc', 'a"b', '"a"b']:
            with self.assertRaises(ErroCSV, msg=txt):
                analisar(txt)

    def test_gerar_roundtrip_e_stdlib(self):
        linhas = [["a", "b,c", 'd"e'], ["x\ny", "", "z"]]
        self.assertEqual(analisar(gerar(linhas)), linhas)
        self.assertEqual(list(csv.reader(io.StringIO(gerar(linhas), newline=""))), linhas)

    def test_separador_invalido(self):
        with self.assertRaises(ValueError):
            analisar("a", '"')


if __name__ == "__main__":
    unittest.main()
