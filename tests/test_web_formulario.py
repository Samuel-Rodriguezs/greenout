import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_formulario import Campo, Formulario


class Cadastro(Formulario):
    campos = {
        "nome": Campo(minimo=2, maximo=10),
        "idade": Campo("int", minimo=0, maximo=150),
        "email": Campo("email"),
        "ativo": Campo("bool"),
        "papel": Campo(escolhas=("admin", "user"), obrigatorio=False, padrao="user"),
        "cep": Campo(obrigatorio=False, regex=r"\d{5}-\d{3}"),
    }


class TestWebFormulario(unittest.TestCase):
    def test_sucesso(self):
        limpos, erros = Cadastro().validar(
            {"nome": " Ana ", "idade": "30", "email": "a@b.com", "ativo": "sim"})
        self.assertEqual(erros, {})
        self.assertEqual(limpos["nome"], "Ana")
        self.assertEqual(limpos["idade"], 30)
        self.assertIs(limpos["ativo"], True)
        self.assertEqual(limpos["papel"], "user")
        self.assertIsNone(limpos["cep"])

    def test_erros_multiplos(self):
        limpos, erros = Cadastro().validar(
            {"nome": "A", "idade": "abc", "email": "x", "papel": "root", "cep": "123"})
        self.assertEqual(limpos, {})
        self.assertEqual(erros["nome"], "mínimo de 2 caracteres")
        self.assertEqual(erros["idade"], "deve ser inteiro")
        self.assertEqual(erros["email"], "e-mail inválido")
        self.assertEqual(erros["papel"], "valor não permitido")
        self.assertEqual(erros["cep"], "formato inválido")

    def test_obrigatorio(self):
        _, erros = Cadastro().validar({})
        self.assertEqual(erros["nome"], "campo obrigatório")
        self.assertNotIn("ativo", erros)

    def test_limites_numericos(self):
        _, erros = Cadastro().validar(
            {"nome": "Ana", "idade": "200", "email": "a@b.co"})
        self.assertEqual(erros, {"idade": "máximo de 150"})

    def test_validador_customizado(self):
        f = Formulario({"s": Campo(validador=lambda v: "proibido" if v == "x" else None)})
        self.assertEqual(f.validar({"s": "x"})[1], {"s": "proibido"})
        self.assertEqual(f.validar({"s": "y"})[0], {"s": "y"})

    def test_bool_invalido(self):
        f = Formulario({"b": Campo("bool")})
        self.assertEqual(f.validar({"b": "talvez"})[1], {"b": "deve ser booleano"})
        self.assertIs(f.validar({"b": "off"})[0]["b"], False)

    def test_float_e_tipo_invalido(self):
        f = Formulario({"p": Campo("float", minimo=0)})
        self.assertEqual(f.validar({"p": "1.5"})[0], {"p": 1.5})
        self.assertEqual(f.validar({"p": "-1"})[1], {"p": "mínimo de 0"})
        with self.assertRaises(ValueError):
            Formulario({"x": Campo("data")})


if __name__ == "__main__":
    unittest.main()
