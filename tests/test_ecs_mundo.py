import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_mundo import Mundo


@dataclass
class Pos:
    x: float = 0.0


@dataclass
class Vel:
    v: float = 0.0


@dataclass
class Morto:
    pass


class TestMundo(unittest.TestCase):
    def test_criar_e_obter(self):
        m = Mundo()
        e = m.criar(Pos(3))
        self.assertTrue(m.existe(e))
        self.assertEqual(m.obter(e, Pos).x, 3)
        self.assertEqual(len(m), 1)

    def test_consulta_por_assinatura(self):
        m = Mundo()
        a = m.criar(Pos(1), Vel(2))
        m.criar(Pos(5))
        c = m.criar(Vel(7), Pos(9))
        res = list(m.consultar(Pos, Vel))
        self.assertEqual([e for e, _ in res], [a, c])
        self.assertEqual(res[1][1][0].x, 9)

    def test_excluir(self):
        m = Mundo()
        a = m.criar(Pos())
        b = m.criar(Pos(), Morto())
        self.assertEqual([e for e, _ in m.consultar(Pos, excluir=(Morto,))], [a])
        self.assertTrue(m.tem(b, Pos, Morto))

    def test_destruir_remove_componentes(self):
        m = Mundo()
        e = m.criar(Pos(), Vel())
        m.destruir(e)
        self.assertFalse(m.existe(e))
        self.assertEqual(list(m.consultar(Pos)), [])
        with self.assertRaises(KeyError):
            m.destruir(e)

    def test_remover_componente(self):
        m = Mundo()
        e = m.criar(Pos(), Vel())
        m.remover(e, Vel)
        self.assertFalse(m.tem(e, Vel))
        with self.assertRaises(KeyError):
            m.remover(e, Vel)
        with self.assertRaises(KeyError):
            m.obter(e, Vel)

    def test_ids_nao_reutilizados(self):
        m = Mundo()
        a = m.criar()
        m.destruir(a)
        self.assertNotEqual(m.criar(), a)

    def test_consulta_vazia_invalida(self):
        with self.assertRaises(ValueError):
            list(Mundo().consultar())


if __name__ == "__main__":
    unittest.main()
