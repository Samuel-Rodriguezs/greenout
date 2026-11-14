import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from proj_templates import renderizar, ErroTemplate


class TestTemplates(unittest.TestCase):
    def test_variavel_simples(self):
        self.assertEqual(renderizar("Ola, {{nome}}!", {"nome": "Ana"}), "Ola, Ana!")

    def test_espacos_e_repeticao(self):
        self.assertEqual(renderizar("{{ x }}-{{x}}", {"x": 1}), "1-1")

    def test_caminho_pontuado_e_lista(self):
        ctx = {"user": {"nome": "Bia", "tags": ["a", "b"]}}
        self.assertEqual(renderizar("{{user.nome}} {{user.tags.1}}", ctx), "Bia b")

    def test_filtros_encadeados(self):
        self.assertEqual(renderizar("{{ n | lower | title }}", {"n": "JOAO SILVA"}), "Joao Silva")
        self.assertEqual(renderizar("{{ l | len }}", {"l": [1, 2, 3]}), "3")

    def test_sem_marcadores(self):
        self.assertEqual(renderizar("texto puro", {}), "texto puro")

    def test_erros(self):
        with self.assertRaises(ErroTemplate):
            renderizar("{{ faltando }}", {})
        with self.assertRaises(ErroTemplate):
            renderizar("{{ x | inexistente }}", {"x": 1})
        with self.assertRaises(ErroTemplate):
            renderizar("{{ l.5 }}", {"l": [1]})
        with self.assertRaises(ErroTemplate):
            renderizar("{{ }}", {})


if __name__ == "__main__":
    unittest.main()
