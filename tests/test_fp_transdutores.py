import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_transdutores import (
    achatar, compor_xf, filtro, largar, mapa, para_lista, pegar,
    pegar_enquanto, somar, transduzir,
)


class TestTransdutores(unittest.TestCase):
    def test_mapa_filtro(self):
        xf = compor_xf(mapa(lambda x: x * 2), filtro(lambda x: x % 3 == 0))
        self.assertEqual(para_lista(xf, range(10)), [0, 6, 12, 18])

    def test_ordem_de_composicao(self):
        a = compor_xf(mapa(lambda x: x + 1), mapa(lambda x: x * 10))
        b = compor_xf(mapa(lambda x: x * 10), mapa(lambda x: x + 1))
        self.assertEqual(para_lista(a, [1]), [20])
        self.assertEqual(para_lista(b, [1]), [11])

    def test_pegar_para_cedo_em_iterador_infinito(self):
        xf = compor_xf(filtro(lambda x: x % 2 == 0), mapa(lambda x: x * x), pegar(4))
        self.assertEqual(para_lista(xf, itertools.count()), [0, 4, 16, 36])

    def test_pegar_nao_consome_alem_do_necessario(self):
        consumidos = []

        def fonte():
            for i in range(100):
                consumidos.append(i)
                yield i
        self.assertEqual(para_lista(pegar(3), fonte()), [0, 1, 2])
        self.assertEqual(consumidos, [0, 1, 2])

    def test_pegar_zero_e_maior_que_tamanho(self):
        self.assertEqual(para_lista(pegar(0), [1, 2]), [])
        self.assertEqual(para_lista(pegar(10), [1, 2]), [1, 2])

    def test_estado_nao_vaza_entre_execucoes(self):
        xf = pegar(2)
        self.assertEqual(para_lista(xf, range(5)), [0, 1])
        self.assertEqual(para_lista(xf, range(5)), [0, 1])
        xd = largar(2)
        self.assertEqual(para_lista(xd, range(5)), [2, 3, 4])
        self.assertEqual(para_lista(xd, range(5)), [2, 3, 4])

    def test_pegar_enquanto_achatar(self):
        self.assertEqual(para_lista(pegar_enquanto(lambda x: x < 3), [1, 2, 3, 1]), [1, 2])
        xf = compor_xf(achatar(), mapa(lambda x: x + 1))
        self.assertEqual(para_lista(xf, [[1, 2], [], [3]]), [2, 3, 4])
        xf2 = compor_xf(achatar(), pegar(3))
        self.assertEqual(para_lista(xf2, [[1, 2], [3, 4], [5]]), [1, 2, 3])

    def test_equivalencia_com_pipeline_tradicional(self):
        dados = list(range(-20, 20))
        esperado = [x * x for x in dados if x > 0][:5]
        xf = compor_xf(filtro(lambda x: x > 0), mapa(lambda x: x * x), pegar(5))
        self.assertEqual(para_lista(xf, dados), esperado)

    def test_somar_e_sem_transdutores(self):
        self.assertEqual(somar(mapa(lambda x: x * 2), [1, 2, 3]), 12)
        self.assertEqual(para_lista(compor_xf(), [1, 2]), [1, 2])
        self.assertEqual(transduzir(mapa(str), lambda a, x: a + x, "", [1, 2]), "12")
        self.assertEqual(para_lista(mapa(abs), []), [])


if __name__ == "__main__":
    unittest.main()
