import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_buffer_pool import BufferCheio, BufferPool


class DiscoFalso:
    def __init__(self, n: int = 20) -> None:
        self.paginas = {i: bytes([i]) * 4 for i in range(n)}
        self.leituras = []
        self.gravacoes = []

    def ler(self, i):
        self.leituras.append(i)
        return self.paginas[i]

    def gravar(self, i, dados):
        self.gravacoes.append(i)
        self.paginas[i] = dados


def usar(pool, i, sujo=False):
    pool.buscar(i)
    pool.liberar(i, sujo)


class TestBufferPool(unittest.TestCase):
    def test_parametros_invalidos(self):
        d = DiscoFalso()
        with self.assertRaises(ValueError):
            BufferPool(0, d.ler, d.gravar)
        with self.assertRaises(ValueError):
            BufferPool(2, d.ler, d.gravar, "fifo")

    def test_acerto_e_falta(self):
        d = DiscoFalso()
        p = BufferPool(2, d.ler, d.gravar)
        usar(p, 1)
        usar(p, 1)
        self.assertEqual((p.faltas, p.acertos), (1, 1))
        self.assertEqual(d.leituras, [1])

    def test_lru_despeja_o_menos_recente(self):
        d = DiscoFalso()
        p = BufferPool(3, d.ler, d.gravar, "lru")
        for i in (1, 2, 3):
            usar(p, i)
        usar(p, 1)          # 2 passa a ser o mais antigo
        usar(p, 4)
        self.assertEqual(p.residentes(), [1, 3, 4])
        self.assertEqual(p.despejos, 1)

    def test_clock_segunda_chance(self):
        d = DiscoFalso()
        p = BufferPool(3, d.ler, d.gravar, "clock")
        for i in (1, 2, 3):
            usar(p, i)
        usar(p, 4)  # todos referenciados: zera bits, despeja o primeiro sob o ponteiro
        self.assertEqual(len(p.residentes()), 3)
        self.assertIn(4, p.residentes())
        self.assertEqual(p.despejos, 1)
        # a próxima vítima é a de bit zerado e não a recém-chegada
        usar(p, 5)
        self.assertIn(5, p.residentes())
        self.assertEqual(p.despejos, 2)

    def test_pagina_suja_e_gravada_ao_despejar(self):
        d = DiscoFalso()
        p = BufferPool(1, d.ler, d.gravar)
        dados = p.buscar(3)
        dados[0] = 99
        p.liberar(3, sujo=True)
        usar(p, 4)
        self.assertEqual(d.gravacoes, [3])
        self.assertEqual(d.paginas[3][0], 99)

    def test_pagina_limpa_nao_e_gravada(self):
        d = DiscoFalso()
        p = BufferPool(1, d.ler, d.gravar)
        usar(p, 1)
        usar(p, 2)
        self.assertEqual(d.gravacoes, [])

    def test_pin_impede_despejo(self):
        for pol in ("lru", "clock"):
            d = DiscoFalso()
            p = BufferPool(2, d.ler, d.gravar, pol)
            p.buscar(1)
            p.buscar(2)
            with self.assertRaises(BufferCheio):
                p.buscar(3)
            p.liberar(2)
            p.buscar(3)
            self.assertEqual(p.residentes(), [1, 3])

    def test_liberar_erros(self):
        d = DiscoFalso()
        p = BufferPool(2, d.ler, d.gravar)
        with self.assertRaises(KeyError):
            p.liberar(5)
        usar(p, 1)
        with self.assertRaises(ValueError):
            p.liberar(1)

    def test_descarregar(self):
        d = DiscoFalso()
        p = BufferPool(3, d.ler, d.gravar)
        for i in (1, 2):
            p.buscar(i)[0] = 7
            p.liberar(i, sujo=True)
        p.descarregar(1)
        self.assertEqual(d.gravacoes, [1])
        p.descarregar()
        self.assertEqual(sorted(d.gravacoes), [1, 2])
        p.descarregar()
        self.assertEqual(len(d.gravacoes), 2)

    def test_falha_de_leitura_nao_corrompe_pool(self):
        d = DiscoFalso(3)
        p = BufferPool(2, d.ler, d.gravar)
        usar(p, 1)
        with self.assertRaises(KeyError):
            p.buscar(50)
        usar(p, 2)
        with self.assertRaises(KeyError):
            p.buscar(50)  # pool cheio: a vítima não pode ser perdida
        self.assertEqual(p.residentes(), [1, 2])
        self.assertEqual(p.buscar(1)[0], 1)


if __name__ == "__main__":
    unittest.main()
