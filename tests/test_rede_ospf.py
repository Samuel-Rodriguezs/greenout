import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_ospf import LSA, LSDB, caminho, lsdb_de_grafo, spf, tabela_de_rotas

# clássico: A-B 7, A-C 9, A-F 14, B-C 10, B-D 15, C-D 11, C-F 2, D-E 6, E-F 9
CLASSICO = [("A", "B", 7), ("A", "C", 9), ("A", "F", 14), ("B", "C", 10), ("B", "D", 15),
            ("C", "D", 11), ("C", "F", 2), ("D", "E", 6), ("E", "F", 9)]


class TestRedeOspf(unittest.TestCase):
    def test_distancias_classicas(self):
        dist, _ = spf(lsdb_de_grafo(CLASSICO), "A")
        self.assertEqual(dist, {"A": 0, "B": 7, "C": 9, "D": 20, "E": 20, "F": 11})

    def test_caminho(self):
        db = lsdb_de_grafo(CLASSICO)
        self.assertEqual(caminho(db, "A", "E"), ["A", "C", "F", "E"])
        self.assertEqual(caminho(db, "A", "A"), ["A"])

    def test_primeiro_salto(self):
        t = tabela_de_rotas(lsdb_de_grafo(CLASSICO), "A")
        self.assertEqual(t["E"], (20, {"C"}))
        self.assertEqual(t["B"], (7, {"B"}))
        self.assertNotIn("A", t)

    def test_ecmp(self):
        db = lsdb_de_grafo([("S", "X", 1), ("S", "Y", 1), ("X", "T", 1), ("Y", "T", 1)])
        custo, saltos = tabela_de_rotas(db, "S")["T"]
        self.assertEqual((custo, saltos), (2, {"X", "Y"}))
        self.assertEqual(caminho(db, "S", "T"), ["S", "X", "T"])

    def test_inalcancavel(self):
        db = lsdb_de_grafo([("A", "B", 1), ("C", "D", 1)])
        self.assertIsNone(caminho(db, "A", "D"))
        self.assertNotIn("C", spf(db, "A")[0])
        with self.assertRaises(KeyError):
            spf(db, "Z")

    def test_lsa_mais_velha_rejeitada(self):
        db = LSDB()
        self.assertTrue(db.instalar(LSA("A", 5, (("B", 1),))))
        self.assertFalse(db.instalar(LSA("A", 5, (("B", 9),))))
        self.assertFalse(db.instalar(LSA("A", 4, (("B", 9),))))
        self.assertTrue(db.instalar(LSA("A", 6, (("B", 2),))))
        self.assertEqual(db.lsas["A"].enlaces, (("B", 2),))

    def test_two_way_check(self):
        db = LSDB()
        db.instalar(LSA("A", 1, (("B", 1),)))
        db.instalar(LSA("B", 1, ()))  # B não anuncia A de volta
        self.assertEqual(db.grafo(), {"A": {}, "B": {}})

    def test_mudanca_de_topologia(self):
        db = lsdb_de_grafo([("A", "B", 1), ("B", "C", 1), ("A", "C", 5)])
        self.assertEqual(spf(db, "A")[0]["C"], 2)
        # B perde o enlace com C: nova LSA com seq maior
        db.instalar(LSA("B", 2, (("A", 1),)))
        self.assertEqual(spf(db, "A")[0]["C"], 5)

    def test_custo_invalido(self):
        with self.assertRaises(ValueError):
            LSDB().instalar(LSA("A", 1, (("B", 0),)))


if __name__ == "__main__":
    unittest.main()
