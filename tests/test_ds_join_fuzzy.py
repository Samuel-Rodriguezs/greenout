import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ds_join_fuzzy import join_fuzzy, similaridade

CLIENTES = [
    {"cliente": "João Silva", "id": 1},
    {"cliente": "Maria Souza", "id": 2},
    {"cliente": "Zé Ninguém", "id": 3},
]
CADASTRO = [
    {"nome": "Joao  Silva", "id": "A"},
    {"nome": "Souza Maria", "id": "B"},
    {"nome": "Pedro Alves", "id": "C"},
]


class TestJoinFuzzy(unittest.TestCase):
    def test_similaridade(self):
        self.assertEqual(similaridade("João Silva", "joao  silva"), 1.0)
        self.assertEqual(similaridade("Maria Souza", "Souza Maria"), 1.0)
        # "abcd" vs "abxd": 3 caracteres em comum -> 2*3/8
        self.assertAlmostEqual(similaridade("abcd", "abxd"), 0.75)
        self.assertEqual(similaridade(None, ""), 1.0)

    def test_inner(self):
        r = join_fuzzy(CLIENTES, CADASTRO, "cliente", "nome", limiar=0.9)
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]["nome"], "Joao  Silva")
        self.assertEqual(r[0]["id"], 1)
        self.assertEqual(r[0]["id_dir"], "A")
        self.assertEqual(r[1]["id_dir"], "B")
        self.assertEqual(r[1]["_similaridade"], 1.0)

    def test_left(self):
        r = join_fuzzy(CLIENTES, CADASTRO, "cliente", "nome", limiar=0.9, how="left")
        self.assertEqual(len(r), 3)
        self.assertIsNone(r[2]["_similaridade"])
        self.assertNotIn("nome", r[2])

    def test_melhor_correspondencia(self):
        esq = [{"k": "banana"}]
        dir_ = [{"k2": "banano"}, {"k2": "banana"}]
        r = join_fuzzy(esq, dir_, "k", "k2", limiar=0.5)
        self.assertEqual(r[0]["k2"], "banana")

    def test_unico(self):
        esq = [{"k": "banana"}, {"k": "bananas"}]
        dir_ = [{"k2": "banana"}]
        livre = join_fuzzy(esq, dir_, "k", "k2", limiar=0.8)
        self.assertEqual(len(livre), 2)
        unico = join_fuzzy(esq, dir_, "k", "k2", limiar=0.8, unico=True)
        self.assertEqual(len(unico), 1)
        self.assertEqual(unico[0]["k"], "banana")

    def test_erros(self):
        with self.assertRaises(ValueError):
            join_fuzzy([], [], "a", "b", how="outer")
        with self.assertRaises(ValueError):
            join_fuzzy([], [], "a", "b", limiar=2)


if __name__ == "__main__":
    unittest.main()
