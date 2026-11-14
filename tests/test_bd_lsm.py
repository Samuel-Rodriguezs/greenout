import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_lsm import LSM


class TestLSM(unittest.TestCase):
    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            LSM(0)
        with self.assertRaises(ValueError):
            LSM(4, 1)

    def test_vazio(self):
        db = LSM()
        self.assertIsNone(db.obter("x"))
        self.assertEqual(list(db.varrer()), [])
        db.descarregar()
        db.compactar()
        self.assertEqual(len(db), 0)

    def test_leitura_na_memtable_e_em_sstables(self):
        db = LSM(limite_memtable=3)
        for i in range(10):
            db.colocar(i, i * 10)
        self.assertGreaterEqual(len(db.tabelas), 3)
        self.assertEqual(db.obter(0), 0)
        self.assertEqual(db.obter(9), 90)
        self.assertEqual(db.obter(99, "nada"), "nada")

    def test_versao_mais_nova_vence(self):
        db = LSM(2, 10)
        db.colocar("k", "v1")
        db.colocar("a", 1)   # descarrega
        db.colocar("k", "v2")
        db.colocar("b", 2)   # descarrega
        self.assertEqual(db.obter("k"), "v2")
        db.colocar("k", "v3")
        self.assertEqual(db.obter("k"), "v3")

    def test_lapide_esconde_versao_antiga(self):
        db = LSM(2, 10)
        db.colocar("k", 1)
        db.colocar("z", 0)
        db.apagar("k")
        self.assertIsNone(db.obter("k"))
        db.descarregar()
        self.assertIsNone(db.obter("k"))
        self.assertNotIn("k", dict(db.varrer()))

    def test_compactacao_remove_lapides_e_reduz_tabelas(self):
        db = LSM(2, 3)
        for i in range(20):
            db.colocar(i, i)
        for i in range(0, 20, 2):
            db.apagar(i)
        db.descarregar()
        db.compactar()
        self.assertEqual(len(db.tabelas), 1)
        self.assertEqual(list(db.tabelas[0].chaves), list(range(1, 20, 2)))
        self.assertGreater(db.compactacoes, 0)

    def test_compactacao_automatica_limita_tabelas(self):
        db = LSM(1, 3)
        for i in range(50):
            db.colocar(i, i)
        self.assertLessEqual(len(db.tabelas), 4)
        self.assertEqual(len(db), 50)

    def test_compactar_tudo_apagado(self):
        db = LSM(1, 2)
        db.colocar("a", 1)
        db.apagar("a")
        db.descarregar()
        db.compactar()
        self.assertEqual(db.tabelas, [])
        self.assertIsNone(db.obter("a"))

    def test_bloom_evita_consultas_ao_indice(self):
        db = LSM(5, 10)
        for i in range(5):
            db.colocar(f"k{i}", i)
        t = db.tabelas[0]
        for i in range(200):
            db.obter(f"ausente{i}")
        self.assertLess(t.consultas_ao_indice, 20)

    def test_varrer_intervalo(self):
        db = LSM(3, 5)
        for i in range(20):
            db.colocar(i, i)
        db.apagar(5)
        self.assertEqual([k for k, _ in db.varrer(3, 8)], [3, 4, 6, 7])
        self.assertEqual([k for k, _ in db.varrer(18)], [18, 19])

    def test_aleatorio_contra_dict(self):
        rnd = random.Random(9)
        db, ref = LSM(5, 3), {}
        for _ in range(2000):
            k = rnd.randrange(80)
            if rnd.random() < 0.7:
                db.colocar(k, rnd.randrange(1000))
                ref[k] = db.obter(k)
            else:
                db.apagar(k)
                ref.pop(k, None)
        for k in range(80):
            self.assertEqual(db.obter(k), ref.get(k))
        self.assertEqual(dict(db.varrer()), ref)


if __name__ == "__main__":
    unittest.main()
