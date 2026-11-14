import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_canal import Canal, CanalFechado, selecionar


class TestCanal(unittest.TestCase):
    def test_com_buffer_fifo(self):
        c = Canal(3)
        for i in range(3):
            c.enviar(i)
        self.assertEqual([c.receber()[0] for _ in range(3)], [0, 1, 2])

    def test_buffer_cheio_bloqueia(self):
        c = Canal(1)
        c.enviar(1)
        with self.assertRaises(TimeoutError):
            c.enviar(2, timeout=0.01)

    def test_sem_buffer_exige_receptor(self):
        c = Canal(0)
        with self.assertRaises(TimeoutError):
            c.enviar(1, timeout=0.01)

    def test_sem_buffer_encontro(self):
        c = Canal(0)
        recebido = []
        t = threading.Thread(target=lambda: recebido.append(c.receber(2)))
        t.start()
        c.enviar("oi", timeout=2)
        t.join(2)
        self.assertEqual(recebido, [("oi", True)])

    def test_fechar_e_iterar(self):
        c = Canal(5)
        for i in range(3):
            c.enviar(i)
        c.fechar()
        self.assertEqual(list(c), [0, 1, 2])
        self.assertEqual(c.receber(), (None, False))
        with self.assertRaises(CanalFechado):
            c.enviar(9)
        with self.assertRaises(CanalFechado):
            c.fechar()

    def test_produtor_consumidor(self):
        c = Canal(0)

        def produtor():
            for i in range(30):
                c.enviar(i, timeout=2)
            c.fechar()

        t = threading.Thread(target=produtor)
        t.start()
        self.assertEqual(list(c), list(range(30)))
        t.join(2)

    def test_fechar_acorda_receptor(self):
        c = Canal(0)
        res = []
        t = threading.Thread(target=lambda: res.append(c.receber(2)))
        t.start()
        c.fechar()
        t.join(2)
        self.assertEqual(res, [(None, False)])


class TestSelecionar(unittest.TestCase):
    def test_recv_pronto(self):
        a, b = Canal(1), Canal(1)
        b.enviar("x")
        self.assertEqual(selecionar([("recv", a), ("recv", b)]), (1, "x", True))

    def test_menor_indice_vence(self):
        a, b = Canal(1), Canal(1)
        a.enviar("a")
        b.enviar("b")
        self.assertEqual(selecionar([("recv", a), ("recv", b)])[:2], (0, "a"))

    def test_padrao(self):
        self.assertEqual(selecionar([("recv", Canal(1))], padrao=True), (-1, None, False))

    def test_timeout(self):
        with self.assertRaises(TimeoutError):
            selecionar([("recv", Canal(1))], timeout=0.01)

    def test_send_com_buffer(self):
        c = Canal(1)
        self.assertEqual(selecionar([("send", c, 7)]), (0, None, True))
        self.assertEqual(c.receber(), (7, True))

    def test_send_cheio_cai_no_recv(self):
        cheio, livre = Canal(1), Canal(1)
        cheio.enviar(0)
        livre.enviar("v")
        i, v, ok = selecionar([("send", cheio, 1), ("recv", livre)])
        self.assertEqual((i, v, ok), (1, "v", True))

    def test_bloqueia_ate_outra_thread(self):
        a, b = Canal(0), Canal(0)
        res = []
        t = threading.Thread(target=lambda: res.append(selecionar([("recv", a), ("recv", b)], timeout=2)))
        t.start()
        b.enviar("tarde", timeout=2)  # só completa porque o select anuncia receptor
        t.join(2)
        self.assertEqual(res, [(1, "tarde", True)])

    def test_recv_em_fechado(self):
        c = Canal(0)
        c.fechar()
        self.assertEqual(selecionar([("recv", c)]), (0, None, False))


if __name__ == "__main__":
    unittest.main()
