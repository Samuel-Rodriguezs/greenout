import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_bloqueios_2pl import S, X, ErroFaseEncolhimento, GerenciadorBloqueios


class TestBloqueios(unittest.TestCase):
    def setUp(self):
        self.g = GerenciadorBloqueios()

    def test_leitores_compartilham(self):
        self.assertTrue(self.g.adquirir(1, "r", S))
        self.assertTrue(self.g.adquirir(2, "r", S))
        self.assertTrue(self.g.adquirir(1, "r", S))  # reentrante

    def test_escritor_conflita(self):
        self.assertTrue(self.g.adquirir(1, "r", X))
        self.assertFalse(self.g.adquirir(2, "r", S))
        self.assertFalse(self.g.adquirir(3, "r", X))
        self.assertEqual(self.g.liberar_todos(1), [2])
        self.assertEqual(self.g.modo(2, "r"), S)
        self.assertEqual(self.g.liberar_todos(2), [3])
        self.assertEqual(self.g.modo(3, "r"), X)

    def test_modo_invalido(self):
        with self.assertRaises(ValueError):
            self.g.adquirir(1, "r", "Z")

    def test_fila_fifo_impede_inanicao_do_escritor(self):
        self.g.adquirir(1, "r", S)
        self.assertFalse(self.g.adquirir(2, "r", X))
        self.assertFalse(self.g.adquirir(3, "r", S))  # não fura o escritor na fila
        self.assertEqual(self.g.liberar_todos(1), [2])

    def test_x_cobre_s(self):
        self.g.adquirir(1, "r", X)
        self.assertTrue(self.g.adquirir(1, "r", S))
        self.assertEqual(self.g.modo(1, "r"), X)

    def test_upgrade_unico_leitor(self):
        self.g.adquirir(1, "r", S)
        self.assertTrue(self.g.adquirir(1, "r", X))
        self.assertEqual(self.g.modo(1, "r"), X)

    def test_upgrade_bloqueado_por_outro_leitor(self):
        self.g.adquirir(1, "r", S)
        self.g.adquirir(2, "r", S)
        self.assertFalse(self.g.adquirir(1, "r", X))
        self.assertEqual(self.g.liberar_todos(2), [1])
        self.assertEqual(self.g.modo(1, "r"), X)

    def test_deadlock_upgrade_duplo(self):
        self.g.adquirir(1, "r", S)
        self.g.adquirir(2, "r", S)
        self.g.adquirir(1, "r", X)
        self.g.adquirir(2, "r", X)
        self.assertEqual(self.g.resolver_deadlock(), 2)
        self.assertEqual(self.g.modo(1, "r"), X)

    def test_fase_de_encolhimento(self):
        self.g.adquirir(1, "a", X)
        self.g.liberar(1, "a")
        with self.assertRaises(ErroFaseEncolhimento):
            self.g.adquirir(1, "b", S)
        self.g.liberar_todos(1)  # fim da transação reinicia o estado
        self.assertTrue(self.g.adquirir(1, "b", S))

    def test_liberar_o_que_nao_tem(self):
        with self.assertRaises(KeyError):
            self.g.liberar(1, "a")

    def test_esperar_duas_vezes_e_erro(self):
        self.g.adquirir(1, "a", X)
        self.assertFalse(self.g.adquirir(2, "a", X))
        with self.assertRaises(RuntimeError):
            self.g.adquirir(2, "b", S)

    def test_sem_deadlock(self):
        self.g.adquirir(1, "a", X)
        self.assertFalse(self.g.adquirir(2, "a", S))
        self.assertIsNone(self.g.detectar_deadlock())
        self.assertIsNone(self.g.resolver_deadlock())

    def test_deadlock_classico_dois_recursos(self):
        self.g.adquirir(1, "a", X)
        self.g.adquirir(2, "b", X)
        self.assertFalse(self.g.adquirir(1, "b", X))
        self.assertFalse(self.g.adquirir(2, "a", X))
        self.assertEqual(sorted(self.g.detectar_deadlock()), [1, 2])
        vitima = self.g.resolver_deadlock()
        self.assertEqual(vitima, 2)
        self.assertEqual(self.g.modo(1, "b"), X)
        self.assertIsNone(self.g.detectar_deadlock())

    def test_deadlock_ciclo_de_tres(self):
        for tx, r in ((1, "a"), (2, "b"), (3, "c")):
            self.g.adquirir(tx, r, X)
        self.g.adquirir(1, "b", X)
        self.g.adquirir(2, "c", X)
        self.g.adquirir(3, "a", X)
        self.assertEqual(sorted(self.g.detectar_deadlock()), [1, 2, 3])
        self.assertEqual(self.g.resolver_deadlock(), 3)
        self.assertIsNone(self.g.detectar_deadlock())
        self.assertEqual(self.g.modo(2, "c"), X)

    def test_espera_nao_ciclica_com_cadeia(self):
        self.g.adquirir(1, "a", X)
        self.g.adquirir(2, "b", X)
        self.g.adquirir(2, "a", X)   # 2 espera 1
        self.g.adquirir(3, "b", X)   # 3 espera 2
        self.assertEqual(self.g.grafo_espera(), {2: {1}, 3: {2}})
        self.assertIsNone(self.g.detectar_deadlock())

    def test_liberar_cancela_espera_pendente(self):
        self.g.adquirir(1, "a", X)
        self.g.adquirir(2, "a", X)
        self.g.liberar_todos(2)
        self.assertEqual(self.g.grafo_espera(), {})
        self.g.liberar_todos(1)
        self.assertTrue(self.g.adquirir(3, "a", X))


if __name__ == "__main__":
    unittest.main()
