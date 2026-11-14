import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_yaml import ErroYaml, carregar, serializar


class TestFmtYaml(unittest.TestCase):
    def test_mapa_simples(self):
        self.assertEqual(carregar("a: 1\nb: texto\nc: true\nd: ~\ne: 2.5"),
                         {"a": 1, "b": "texto", "c": True, "d": None, "e": 2.5})

    def test_aninhado_e_listas(self):
        doc = "nome: x\nitens:\n  - 1\n  - dois\nsub:\n  k: v\n  lista:\n    - a\n    - b\n"
        self.assertEqual(carregar(doc), {"nome": "x", "itens": [1, "dois"],
                                         "sub": {"k": "v", "lista": ["a", "b"]}})

    def test_lista_na_mesma_indentacao(self):
        self.assertEqual(carregar("a:\n- 1\n- 2\nb: 3"), {"a": [1, 2], "b": 3})

    def test_lista_de_mapas(self):
        doc = "- nome: a\n  idade: 1\n- nome: b\n  idade: 2\n"
        self.assertEqual(carregar(doc), [{"nome": "a", "idade": 1}, {"nome": "b", "idade": 2}])

    def test_comentarios_e_aspas(self):
        self.assertEqual(carregar("# c\na: 'x # y'  # fim\nb: \"1\"\n---\n"), {"a": "x # y", "b": "1"})

    def test_fluxo(self):
        self.assertEqual(carregar("a: [1, 2, [3, 4]]\nb: {x: 1, y: 'a,b'}"),
                         {"a": [1, 2, [3, 4]], "b": {"x": 1, "y": "a,b"}})

    def test_escalar_raiz_e_vazio(self):
        self.assertEqual(carregar("42"), 42)
        self.assertIsNone(carregar("\n# nada\n"))

    def test_valor_nulo_sem_filhos(self):
        self.assertEqual(carregar("a:\nb: 1"), {"a": None, "b": 1})

    def test_malformados(self):
        for ruim in ["a: 1\n  b: 2", "a: 1\na: 2", "\tx: 1", "a: [1, 2", "só texto\noutro", "a: 'abc",
                     "a: 1\nsem_dois_pontos"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroYaml):
                    carregar(ruim)

    def test_ida_e_volta(self):
        dados = {"a": 1, "b": [1, {"x": "y", "z": [1, 2]}, "t"], "c": {"d": None, "e": "1", "f": ""}, "g": []}
        self.assertEqual(carregar(serializar(dados)), dados)


if __name__ == "__main__":
    unittest.main()
