import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_json import ErroJSON, carregar, serializar


class TestJSON(unittest.TestCase):
    def test_valores_simples(self):
        self.assertIsNone(carregar("null"))
        self.assertIs(carregar(" true "), True)
        self.assertEqual(carregar("-12"), -12)
        self.assertEqual(carregar("1.5e2"), 150.0)
        self.assertEqual(carregar('"olá"'), "olá")

    def test_estruturas(self):
        txt = '{"a": [1, 2, {"b": null}], "c": "x", "d": {}, "e": []}'
        self.assertEqual(carregar(txt), json.loads(txt))

    def test_escapes(self):
        self.assertEqual(carregar(r'"a\n\t\"\\é"'), 'a\n\t"\\é')
        self.assertEqual(carregar(r'"😀"'), "\U0001F600")

    def test_concordancia_com_stdlib(self):
        for txt in ["[0, -0.5, 1e-3, 10E+2]", '{"k": [true, false]}', "[[[]]]"]:
            self.assertEqual(carregar(txt), json.loads(txt))

    def test_roundtrip(self):
        obj = {"nome": "Ana\n", "n": [1, 2.5, None, True], "o": {"x": "\u0001"}}
        self.assertEqual(carregar(serializar(obj)), obj)
        self.assertEqual(json.loads(serializar(obj)), obj)

    def test_erros_de_sintaxe(self):
        invalidos = ["", "[1,", "{'a':1}", '{"a" 1}', "[1 2]", "01", "1.", "tru", '"abc',
                     '{"a":1,}', "[1,]", "1 2", '"\\x"', '"\\u12"', "-", '"a\nb"']
        for txt in invalidos:
            with self.assertRaises(ErroJSON, msg=repr(txt)):
                carregar(txt)

    def test_posicao_no_erro(self):
        with self.assertRaises(ErroJSON) as ctx:
            carregar("[1, @]")
        self.assertIn("posição 4", str(ctx.exception))

    def test_aninhamento_excessivo(self):
        with self.assertRaises(ErroJSON):
            carregar("[" * 2000 + "]" * 2000)

    def test_serializar_tipo_invalido(self):
        with self.assertRaises(TypeError):
            serializar({1, 2})


if __name__ == "__main__":
    unittest.main()
