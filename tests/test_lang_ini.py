import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_ini import ErroConfig, analisar

EXEMPLO = """
titulo = "Meu app"   # comentário
debug = true

[servidor]
host = "localhost"
porta = 8_080
pesos = [1, 2.5, "a,b"]

[servidor.tls]
ativo = false
; outro comentário
versoes = []
"""


class TestINI(unittest.TestCase):
    def test_exemplo_completo(self):
        r = analisar(EXEMPLO)
        self.assertEqual(r["titulo"], "Meu app")
        self.assertIs(r["debug"], True)
        self.assertEqual(r["servidor"]["porta"], 8080)
        self.assertEqual(r["servidor"]["pesos"], [1, 2.5, "a,b"])
        self.assertEqual(r["servidor"]["tls"], {"ativo": False, "versoes": []})

    def test_texto_puro_estilo_ini(self):
        self.assertEqual(analisar("[a]\nnome = Ana Maria"), {"a": {"nome": "Ana Maria"}})

    def test_comentario_dentro_de_string(self):
        self.assertEqual(analisar('x = "a # b"'), {"x": "a # b"})

    def test_lista_com_virgula_final(self):
        self.assertEqual(analisar("x = [1, 2,]"), {"x": [1, 2]})

    def test_vazio(self):
        self.assertEqual(analisar("\n  \n# nada"), {})

    def test_erros_com_linha(self):
        casos = {
            "[sec": "linha 1",
            "a = 1\nb": "linha 2",
            "a = ": "linha 1",
            'a = "abc': "linha 1",
            "a = [1, 2": "linha 1",
            "[]": "linha 1",
            "a = 1\na = 2": "linha 2",
            "[x]\n[x]": "linha 2",
            "b c = 1": "linha 1",
        }
        for txt, esperado in casos.items():
            with self.assertRaises(ErroConfig, msg=txt) as ctx:
                analisar(txt)
            self.assertIn(esperado, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
