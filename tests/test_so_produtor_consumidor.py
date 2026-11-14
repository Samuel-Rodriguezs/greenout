import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_produtor_consumidor import simular


class TestProdutorConsumidor(unittest.TestCase):
    def test_consumidor_lento_enche_buffer(self):
        r = simular(itens=5, capacidade=2, t_producao=1, t_consumo=3)
        self.assertEqual(
            r.consumidos,
            [(1, 0, 4), (2, 0, 7), (3, 0, 10), (4, 0, 13), (5, 0, 16)],
        )
        self.assertEqual(r.fim, 16)
        self.assertEqual(r.max_ocupacao, 2)
        self.assertEqual(r.produtor_bloqueado, 2)  # item 5 espera de t=5 a t=7
        self.assertEqual(r.consumidor_ocioso, 1)  # só antes do primeiro item

    def test_log_do_bloqueio(self):
        r = simular(5, 2, 1, 3)
        self.assertIn((5, "produtor bloqueia com item 5"), r.log)
        self.assertIn((7, "produtor libera item 5"), r.log)

    def test_produtor_lento_deixa_consumidor_ocioso(self):
        r = simular(itens=3, capacidade=1, t_producao=4, t_consumo=1)
        self.assertEqual(r.consumidos, [(1, 0, 5), (2, 0, 9), (3, 0, 13)])
        self.assertEqual(r.produtor_bloqueado, 0)
        self.assertEqual(r.max_ocupacao, 0)  # item entregue direto ao consumidor
        self.assertEqual(r.consumidor_ocioso, 4 + 3 + 3)

    def test_dois_consumidores(self):
        r = simular(itens=4, capacidade=2, t_producao=1, t_consumo=2, consumidores=2)
        self.assertEqual(r.consumidos, [(1, 0, 3), (2, 1, 4), (3, 0, 5), (4, 1, 6)])
        self.assertEqual(r.fim, 6)
        self.assertEqual(r.consumidor_ocioso, 3)
        self.assertEqual(r.produtor_bloqueado, 0)

    def test_buffer_de_um_com_consumidor_lento(self):
        r = simular(itens=3, capacidade=1, t_producao=1, t_consumo=5)
        # t1: c0 pega 1 (fim 6); t2: buffer [2]; t3: item 3 bloqueia até t6
        self.assertEqual([c[2] for c in r.consumidos], [6, 11, 16])
        self.assertEqual(r.produtor_bloqueado, 3)

    def test_conservacao_de_itens(self):
        r = simular(20, 3, 2, 5, consumidores=2)
        self.assertEqual(sorted(i for i, _, _ in r.consumidos), list(range(1, 21)))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            simular(0, 1, 1, 1)
        with self.assertRaises(ValueError):
            simular(1, 1, 1, 1, consumidores=0)


if __name__ == "__main__":
    unittest.main()
