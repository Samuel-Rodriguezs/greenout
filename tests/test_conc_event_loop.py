import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_event_loop import Dormir, Esperar, EventLoop


class TestEventLoop(unittest.TestCase):
    def test_dormir_ordena_por_tempo(self):
        loop = EventLoop()
        log = []

        def tarefa(nome, t):
            yield Dormir(t)
            log.append((nome, loop.agora))

        loop.criar_tarefa(tarefa("a", 3))
        loop.criar_tarefa(tarefa("b", 1))
        loop.criar_tarefa(tarefa("c", 2))
        fim = loop.executar()
        self.assertEqual(log, [("b", 1), ("c", 2), ("a", 3)])
        self.assertEqual(fim, 3)

    def test_ceder_intercala(self):
        loop = EventLoop()
        log = []

        def t(nome):
            for i in range(3):
                log.append(f"{nome}{i}")
                yield

        loop.criar_tarefa(t("x"))
        loop.criar_tarefa(t("y"))
        loop.executar()
        self.assertEqual(log, ["x0", "y0", "x1", "y1", "x2", "y2"])

    def test_esperar_resultado(self):
        loop = EventLoop()

        def filho():
            yield Dormir(5)
            return 99

        f = loop.criar_tarefa(filho())
        capturado = []

        def pai():
            alvo = yield Esperar(f)
            capturado.append((alvo.resultado, loop.agora))

        loop.criar_tarefa(pai())
        loop.executar()
        self.assertEqual(capturado, [(99, 5)])

    def test_esperar_tarefa_ja_pronta(self):
        loop = EventLoop()

        def rapido():
            return 1
            yield  # pragma: no cover

        f = loop.criar_tarefa(rapido())
        res = []

        def pai():
            yield Dormir(1)
            alvo = yield Esperar(f)
            res.append(alvo.resultado)

        loop.criar_tarefa(pai())
        loop.executar()
        self.assertEqual(res, [1])

    def test_excecao_fica_na_tarefa(self):
        loop = EventLoop()

        def ruim():
            yield
            raise ValueError("boom")

        t = loop.criar_tarefa(ruim())
        loop.executar()
        self.assertTrue(t.pronta)
        self.assertIsInstance(t.erro, ValueError)

    def test_tempo_virtual_paralelo(self):
        loop = EventLoop()

        def t():
            yield Dormir(10)

        for _ in range(100):
            loop.criar_tarefa(t())
        self.assertEqual(loop.executar(), 10)  # concorrentes, não soma 1000


if __name__ == "__main__":
    unittest.main()
