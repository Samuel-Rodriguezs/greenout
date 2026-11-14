import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_csv_json import ErroCsv, converter, csv_para_json, json_string, ler_registros


class TestFmtCsvJson(unittest.TestCase):
    def test_registros_basicos(self):
        self.assertEqual(list(ler_registros(["a,b\n1,2\n"])), [["a", "b"], ["1", "2"]])
        self.assertEqual(list(ler_registros(["a;b\r\n1;2"], ";")), [["a", "b"], ["1", "2"]])

    def test_aspas_virgula_e_quebra(self):
        regs = list(ler_registros(['x,"a, ""b""",y\n"l1\nl2",2,3\n']))
        self.assertEqual(regs, [["x", 'a, "b"', "y"], ["l1\nl2", "2", "3"]])

    def test_campos_vazios_e_linhas_em_branco(self):
        self.assertEqual(list(ler_registros(["a,,c\n\n,\n"])), [["a", "", "c"], ["", ""]])

    def test_streaming_em_pedacos_minusculos(self):
        texto = 'n,v\r\n"a,b",1\r\nc,"2"\r\n'
        pedacos = list(texto)  # um caractere por vez, inclusive \r e \n separados
        self.assertEqual(list(ler_registros(pedacos)), list(ler_registros([texto])))

    def test_json_valido_e_tipos(self):
        texto = 'nome,idade,ativo,nota,cod\nAna,30,true,9.5,007\n"B ""x""",,false,-1,\n'
        saida = csv_para_json(texto)
        self.assertEqual(json.loads(saida), [
            {"nome": "Ana", "idade": 30, "ativo": True, "nota": 9.5, "cod": "007"},
            {"nome": 'B "x"', "idade": None, "ativo": False, "nota": -1, "cod": None},
        ])

    def test_sem_inferencia_e_sem_cabecalho(self):
        self.assertEqual(json.loads(csv_para_json("1,2\n3,4", inferir_tipos=False, cabecalho=False)),
                         [["1", "2"], ["3", "4"]])

    def test_gerador_entrega_aos_poucos(self):
        g = converter(iter(["a\n", "1\n", "2\n"]))
        self.assertEqual(next(g), "[")
        self.assertEqual(next(g), '{"a":1}')
        self.assertEqual(next(g), ',{"a":2}')
        self.assertEqual(next(g), "]")

    def test_json_string(self):
        s = 'a"b\\c\n\t\x01é'
        self.assertEqual(json.loads(json_string(s)), s)

    def test_vazio(self):
        self.assertEqual(csv_para_json(""), "[]")
        self.assertEqual(csv_para_json("a,b\n"), "[]")

    def test_malformados(self):
        casos = ['a,b\n"aberta,1', 'a,b\n"x"y,1', "a,b\n1,2,3", "a,a\n1,2", "a,b\n1"]
        for ruim in casos:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroCsv):
                    csv_para_json(ruim)


if __name__ == "__main__":
    unittest.main()
