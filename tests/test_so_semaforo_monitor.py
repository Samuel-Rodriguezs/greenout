import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_semaforo_monitor import (
    ErroSincronizacao,
    Sistema,
    difundir,
    down,
    entrar,
    esperar,
    passo,
    sair,
    sinalizar,
    up,
)


def secao(nome, mutex=None):
    def corpo():
        if mutex:
            yield down(mutex)
        yield passo(nome + "1")
        yield passo(nome + "2")
        if mutex:
            yield up(mutex)

    return corpo


class TestSemaforo(unittest.TestCase):
    def test_sem_exclusao_ha_intercalacao(self):
        s = Sistema()
        s.spawn("A", secao("A"))
        s.spawn("B", secao("B"))
        self.assertEqual(s.executar(), "fim")
        self.assertEqual(s.eventos(), ["A1", "B1", "A2", "B2"])

    def test_mutex_serializa_secao_critica(self):
        s = Sistema()
        s.semaforo("m", 1)
        s.spawn("A", secao("A", "m"))
        s.spawn("B", secao("B", "m"))
        self.assertEqual(s.executar(), "fim")
        self.assertEqual(s.eventos(), ["A1", "A2", "B1", "B2"])
        self.assertIn((1, "B", "bloqueia em semáforo m"), s.trace)
        self.assertEqual(s.semaforos["m"].valor, 1)

    def test_semaforo_contador(self):
        s = Sistema()
        s.semaforo("vagas", 2)
        for n in ("P1", "P2", "P3"):
            s.spawn(n, secao(n, "vagas"))
        self.assertEqual(s.executar(), "fim")
        # P3 só entra depois que P1 libera uma vaga
        self.assertEqual(s.eventos(), ["P11", "P21", "P12", "P22", "P31", "P32"])
        self.assertEqual(s.semaforos["vagas"].valor, 2)

    def test_deadlock_por_ordem_oposta(self):
        s = Sistema()
        s.semaforo("a", 1)
        s.semaforo("b", 1)

        def p1():
            yield down("a")
            yield passo("p1 tem a")
            yield down("b")

        def p2():
            yield down("b")
            yield passo("p2 tem b")
            yield down("a")

        s.spawn("P1", p1)
        s.spawn("P2", p2)
        self.assertEqual(s.executar(), "deadlock")
        self.assertEqual(s.bloqueados(), ["P1", "P2"])

    def test_fila_fifo_de_espera(self):
        s = Sistema()
        s.semaforo("s", 0)

        def espera(n):
            def corpo():
                yield down("s")
                yield passo(n)

            return corpo

        def libera():
            for _ in range(2):
                yield up("s")

        s.spawn("W1", espera("w1"))
        s.spawn("W2", espera("w2"))
        s.spawn("L", libera)
        self.assertEqual(s.executar(), "fim")
        self.assertEqual(s.eventos(), ["w1", "w2"])

    def test_limite_de_passos(self):
        s = Sistema()

        def eterno():
            while True:
                yield passo("x")

        s.spawn("E", eterno)
        self.assertEqual(s.executar(max_passos=5), "limite")


class TestMonitor(unittest.TestCase):
    def test_caixa_de_um_item(self):
        s = Sistema()
        s.monitor("m", ("cheio", "vazio"))
        caixa = {"item": None}
        consumidos = []

        def produtor():
            for i in (1, 2, 3):
                yield entrar("m")
                while caixa["item"] is not None:
                    yield esperar("m", "vazio")
                caixa["item"] = i
                yield sinalizar("m", "cheio")
                yield sair("m")

        def consumidor():
            for _ in range(3):
                yield entrar("m")
                while caixa["item"] is None:
                    yield esperar("m", "cheio")
                consumidos.append(caixa["item"])
                caixa["item"] = None
                yield sinalizar("m", "vazio")
                yield sair("m")

        s.spawn("prod", produtor)
        s.spawn("cons", consumidor)
        self.assertEqual(s.executar(), "fim")
        self.assertEqual(consumidos, [1, 2, 3])
        self.assertIsNone(s.monitores["m"].dono)

    def test_exclusao_mutua_no_monitor(self):
        s = Sistema()
        s.monitor("m")

        def usa(n):
            def corpo():
                yield entrar("m")
                yield passo(n + "a")
                yield passo(n + "b")
                yield sair("m")

            return corpo

        s.spawn("A", usa("A"))
        s.spawn("B", usa("B"))
        s.executar()
        self.assertEqual(s.eventos(), ["Aa", "Ab", "Ba", "Bb"])

    def test_difundir_acorda_todos(self):
        s = Sistema()
        s.monitor("m", ("go",))
        pronto = {"v": False}

        def espera(n):
            def corpo():
                yield entrar("m")
                while not pronto["v"]:
                    yield esperar("m", "go")
                yield passo(n)
                yield sair("m")

            return corpo

        def libera():
            yield entrar("m")
            pronto["v"] = True
            yield difundir("m", "go")
            yield sair("m")

        s.spawn("W1", espera("w1"))
        s.spawn("W2", espera("w2"))
        s.spawn("L", libera)
        self.assertEqual(s.executar(), "fim")
        self.assertEqual(s.eventos(), ["w1", "w2"])

    def test_sinalizar_sem_possuir_monitor(self):
        s = Sistema()
        s.monitor("m", ("c",))

        def mau():
            yield sinalizar("m", "c")

        s.spawn("X", mau)
        with self.assertRaises(ErroSincronizacao):
            s.executar()


if __name__ == "__main__":
    unittest.main()
