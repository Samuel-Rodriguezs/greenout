import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_sql import ErroSQL, consultar

BANCO = {
    "pessoas": [
        {"nome": "Ana", "idade": 30, "cidade": "Recife"},
        {"nome": "Bruno", "idade": 25, "cidade": "Natal"},
        {"nome": "Carla", "idade": 35, "cidade": "Recife"},
        {"nome": "Davi", "idade": None, "cidade": "Natal"},
        {"nome": "O'Neil", "idade": 41, "cidade": None},
    ]
}


def nomes(sql: str) -> list[str]:
    return [r["nome"] for r in consultar(sql, BANCO)]


class TestSQL(unittest.TestCase):
    def test_select_estrela(self):
        self.assertEqual(len(consultar("SELECT * FROM pessoas", BANCO)), 5)

    def test_projecao(self):
        self.assertEqual(consultar("select nome, idade from pessoas limit 1", BANCO),
                         [{"nome": "Ana", "idade": 30}])

    def test_where_comparacoes(self):
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE idade >= 30"), ["Ana", "Carla", "O'Neil"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE cidade = 'Natal'"), ["Bruno", "Davi"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE idade <> 30 AND idade < 40"), ["Bruno", "Carla"])

    def test_and_or_not_parenteses(self):
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE cidade = 'Recife' OR idade = 25"),
                         ["Ana", "Bruno", "Carla"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE NOT (cidade = 'Recife' OR cidade = 'Natal')"),
                         ["O'Neil"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE (idade > 26 OR cidade = 'Natal') AND cidade = 'Recife'"),
                         ["Ana", "Carla"])

    def test_like_in_null(self):
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE nome LIKE '%a'"), ["Ana", "Carla"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE nome LIKE '_ru%'"), ["Bruno"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE cidade IN ('Natal', 'Recife') AND idade IS NOT NULL"),
                         ["Ana", "Bruno", "Carla"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE nome NOT IN ('Ana', 'Davi')"),
                         ["Bruno", "Carla", "O'Neil"])
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE idade IS NULL"), ["Davi"])

    def test_string_com_aspas_escapadas(self):
        self.assertEqual(nomes("SELECT nome FROM pessoas WHERE nome = 'O''Neil'"), ["O'Neil"])

    def test_order_by_nulls_por_ultimo(self):
        self.assertEqual(nomes("SELECT nome FROM pessoas ORDER BY idade"), ["Bruno", "Ana", "Carla", "O'Neil", "Davi"])
        self.assertEqual(nomes("SELECT nome FROM pessoas ORDER BY idade DESC LIMIT 2"), ["O'Neil", "Carla"])

    def test_null_nao_satisfaz_comparacao(self):
        self.assertNotIn("Davi", nomes("SELECT nome FROM pessoas WHERE idade < 100"))
        self.assertNotIn("Davi", nomes("SELECT nome FROM pessoas WHERE idade != 5"))

    def test_nao_altera_origem(self):
        r = consultar("SELECT * FROM pessoas", BANCO)
        r[0]["nome"] = "X"
        self.assertEqual(BANCO["pessoas"][0]["nome"], "Ana")

    def test_erros(self):
        invalidos = [
            "", "SELECT FROM pessoas", "SELECT * pessoas", "SELECT * FROM nada",
            "SELECT * FROM pessoas WHERE", "SELECT * FROM pessoas WHERE idade",
            "SELECT * FROM pessoas WHERE idade > ", "SELECT * FROM pessoas LIMIT -1",
            "SELECT * FROM pessoas LIMIT x", "SELECT * FROM pessoas extra",
            "SELECT * FROM pessoas WHERE (idade > 1", "SELECT * FROM pessoas WHERE nome = 'abc",
            "SELECT * FROM pessoas WHERE nome > 3", "SELECT * FROM pessoas WHERE idade IN 1",
            "SELECT * FROM pessoas ORDER idade", "SELECT * FROM pessoas WHERE idade NOT 3",
        ]
        for sql in invalidos:
            with self.assertRaises(ErroSQL, msg=sql):
                consultar(sql, BANCO)


if __name__ == "__main__":
    unittest.main()
