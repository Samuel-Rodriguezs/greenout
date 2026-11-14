import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_processos import (
    SIG_DFL,
    SIG_IGN,
    SIGCHLD,
    SIGCONT,
    SIGINT,
    SIGKILL,
    SIGSTOP,
    SIGTERM,
    SIGUSR1,
    ErroECHILD,
    Kernel,
    ProcessoInexistente,
    Saida,
)


class TestProcessos(unittest.TestCase):
    def test_fork_exec(self):
        k = Kernel()
        filho = k.fork(1)
        self.assertEqual(filho, 2)
        self.assertEqual(k.fork(1), 3)
        k.exec(2, "ls")
        self.assertEqual(
            k.ps(), [(1, 0, "pronto", "init"), (2, 1, "pronto", "ls"), (3, 1, "pronto", "init")]
        )

    def test_wait_colhe_zumbi(self):
        k = Kernel()
        f = k.fork(1)
        k.exit(f, 3)
        self.assertEqual(k.tabela[f].estado, "zumbi")
        self.assertEqual(k.wait(1), Saida(f, 3))
        self.assertNotIn(f, k.tabela)
        with self.assertRaises(ErroECHILD):
            k.wait(1)

    def test_wait_bloqueia_ate_o_filho_sair(self):
        k = Kernel()
        f = k.fork(1)
        self.assertIsNone(k.wait(1))
        self.assertEqual(k.tabela[1].estado, "bloqueado")
        k.exit(f, 7)
        self.assertEqual(k.tabela[1].estado, "pronto")
        self.assertEqual(k.tabela[1].wait_resultado, Saida(f, 7))
        self.assertNotIn(f, k.tabela)

    def test_waitpid_especifico(self):
        k = Kernel()
        a, b = k.fork(1), k.fork(1)
        k.exit(a, 1)
        self.assertIsNone(k.wait(1, filho=b))  # a é zumbi, mas só interessa b
        k.exit(b, 2)
        self.assertEqual(k.tabela[1].wait_resultado, Saida(b, 2))
        self.assertEqual(k.wait(1), Saida(a, 1))

    def test_orfaos_sao_adotados_pelo_init(self):
        k = Kernel()
        p2 = k.fork(1)
        p3 = k.fork(p2)
        k.exit(p2, 0)
        self.assertEqual(k.tabela[p3].ppid, 1)
        self.assertEqual(k.wait(1), Saida(p2, 0))
        k.exit(p3, 5)
        self.assertEqual(k.wait(1), Saida(p3, 5))

    def test_sigterm_padrao_termina(self):
        k = Kernel()
        f = k.fork(1)
        k.kill(f, SIGTERM)
        self.assertEqual(k.wait(1), Saida(f, 143, SIGTERM))

    def test_handler_captura_e_processo_continua(self):
        k = Kernel()
        f = k.fork(1)
        recebidos = []
        k.sigaction(f, SIGUSR1, recebidos.append)
        k.kill(f, SIGUSR1)
        k.kill(f, SIGUSR1)
        self.assertEqual(recebidos, [SIGUSR1, SIGUSR1])
        self.assertEqual(k.tabela[f].estado, "pronto")

    def test_sigkill_e_sigstop_nao_podem_ser_capturados(self):
        k = Kernel()
        f = k.fork(1)
        with self.assertRaises(ValueError):
            k.sigaction(f, SIGKILL, lambda s: None)
        with self.assertRaises(ValueError):
            k.sigaction(f, SIGSTOP, SIG_IGN)
        with self.assertRaises(ValueError):
            k.bloquear(f, SIGKILL)
        k.kill(f, SIGKILL)
        self.assertEqual(k.wait(1), Saida(f, 137, SIGKILL))

    def test_sinal_ignorado(self):
        k = Kernel()
        f = k.fork(1)
        k.sigaction(f, SIGINT, SIG_IGN)
        k.kill(f, SIGINT)
        self.assertEqual(k.tabela[f].estado, "pronto")
        k.sigaction(f, SIGINT, SIG_DFL)
        k.kill(f, SIGINT)
        self.assertEqual(k.tabela[f].estado, "zumbi")

    def test_bloqueado_fica_pendente_sem_acumular(self):
        k = Kernel()
        f = k.fork(1)
        recebidos = []
        k.sigaction(f, SIGUSR1, recebidos.append)
        k.bloquear(f, SIGUSR1)
        k.kill(f, SIGUSR1)
        k.kill(f, SIGUSR1)
        self.assertEqual(recebidos, [])
        self.assertEqual(k.tabela[f].pendentes, {SIGUSR1})
        k.desbloquear(f, SIGUSR1)
        self.assertEqual(recebidos, [SIGUSR1])  # entregue uma única vez

    def test_stop_e_cont(self):
        k = Kernel()
        f = k.fork(1)
        k.kill(f, SIGSTOP)
        self.assertEqual(k.tabela[f].estado, "parado")
        k.kill(f, SIGCONT)
        self.assertEqual(k.tabela[f].estado, "pronto")

    def test_sigchld_notifica_o_pai(self):
        k = Kernel()
        f = k.fork(1)
        avisos = []
        k.sigaction(1, SIGCHLD, avisos.append)
        k.exit(f, 0)
        self.assertEqual(avisos, [SIGCHLD])

    def test_filho_herda_handlers_e_exec_restaura(self):
        k = Kernel()
        k.sigaction(1, SIGUSR1, lambda s: None)
        k.sigaction(1, SIGINT, SIG_IGN)
        f = k.fork(1)
        self.assertEqual(set(k.tabela[f].handlers), {SIGUSR1, SIGINT})
        k.exec(f, "prog")
        self.assertEqual(k.tabela[f].handlers, {SIGINT: SIG_IGN})  # capturado volta ao padrão

    def test_pendentes_nao_sao_herdados_no_fork(self):
        k = Kernel()
        k.bloquear(1, SIGUSR1)
        k.kill(1, SIGUSR1)
        f = k.fork(1)
        self.assertEqual(k.tabela[f].pendentes, set())
        self.assertEqual(k.tabela[f].bloqueados, {SIGUSR1})

    def test_sinal_para_zumbi_e_erros(self):
        k = Kernel()
        f = k.fork(1)
        k.exit(f)
        k.kill(f, SIGTERM)  # ignorado
        with self.assertRaises(ProcessoInexistente):
            k.kill(99, SIGTERM)
        with self.assertRaises(ProcessoInexistente):
            k.fork(f)
        with self.assertRaises(ValueError):
            k.exit(1)
        k.kill(1, SIGTERM)  # init sobrevive ao padrão
        self.assertEqual(k.tabela[1].estado, "pronto")


if __name__ == "__main__":
    unittest.main()
