import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_pipes import Bloquearia, ErroFD, PipeQuebrado, Sistema, TabelaFDs


class TestPipes(unittest.TestCase):
    def setUp(self):
        self.sis = Sistema()
        self.pai = TabelaFDs(self.sis)

    def test_fd_padrao_e_menor_livre(self):
        self.assertEqual(sorted(self.pai.fds), [0, 1, 2])
        r, w = self.pai.criar_pipe()
        self.assertEqual((r, w), (3, 4))
        self.pai.fechar(3)
        self.assertEqual(self.pai.abrir("x", "w"), 3)

    def test_pai_filho_pelo_pipe(self):
        r, w = self.pai.criar_pipe()
        filho = self.pai.clonar()  # fork
        filho.fechar(r)
        self.pai.fechar(w)
        filho.escrever(w, b"ola pai")
        self.assertEqual(self.pai.ler(r, 100), b"ola pai")
        with self.assertRaises(Bloquearia):  # filho ainda tem a ponta de escrita
            self.pai.ler(r, 100)
        filho.fechar(w)
        self.assertEqual(self.pai.ler(r, 100), b"")  # EOF

    def test_eof_so_com_todos_os_escritores_fechados(self):
        r, w = self.pai.criar_pipe()
        filho = self.pai.clonar()
        self.pai.fechar(w)
        with self.assertRaises(Bloquearia):
            self.pai.ler(r, 1)  # o filho herdou a ponta de escrita
        filho.fechar_todos()
        self.assertEqual(self.pai.ler(r, 1), b"")

    def test_pipe_quebrado(self):
        r, w = self.pai.criar_pipe()
        self.pai.fechar(r)
        with self.assertRaises(PipeQuebrado):
            self.pai.escrever(w, b"x")

    def test_pipe_cheio_escrita_parcial(self):
        r, w = self.pai.criar_pipe(capacidade=4)
        self.assertEqual(self.pai.escrever(w, b"abcdef"), 4)
        with self.assertRaises(Bloquearia):
            self.pai.escrever(w, b"g")
        self.assertEqual(self.pai.ler(r, 2), b"ab")
        self.assertEqual(self.pai.escrever(w, b"gh"), 2)
        self.assertEqual(self.pai.ler(r, 10), b"cdgh")

    def test_redirecionar_saida_para_arquivo(self):
        fd = self.pai.abrir("saida.txt", "w")
        self.pai.dup2(fd, 1)
        self.pai.fechar(fd)
        self.pai.escrever(1, b"echo oi\n")
        self.assertEqual(bytes(self.sis.arquivos["saida.txt"]), b"echo oi\n")
        self.assertEqual(bytes(self.sis.stdout), b"")

    def test_anexar_e_truncar(self):
        for modo, dados in (("w", b"AAA"), ("a", b"BB")):
            fd = self.pai.abrir("f", modo)
            self.pai.escrever(fd, dados)
            self.pai.fechar(fd)
        self.assertEqual(bytes(self.sis.arquivos["f"]), b"AAABB")
        fd = self.pai.abrir("f", "w")
        self.pai.fechar(fd)
        self.assertEqual(bytes(self.sis.arquivos["f"]), b"")

    def test_redirecionar_entrada_de_arquivo(self):
        self.sis.arquivos["in"] = bytearray(b"linha1\nlinha2\n")
        fd = self.pai.abrir("in", "r")
        self.pai.dup2(fd, 0)
        self.assertEqual(self.pai.ler(0, 6), b"linha1")
        self.assertEqual(self.pai.ler_tudo(0), b"\nlinha2\n")

    def test_dup_compartilha_posicao(self):
        self.sis.arquivos["f"] = bytearray(b"abcdef")
        fd = self.pai.abrir("f", "r")
        fd2 = self.pai.dup(fd)
        self.assertEqual(self.pai.ler(fd, 2), b"ab")
        self.assertEqual(self.pai.ler(fd2, 2), b"cd")

    def test_erros_de_fd(self):
        with self.assertRaises(ErroFD):
            self.pai.ler(9, 1)
        with self.assertRaises(ErroFD):
            self.pai.escrever(0, b"x")  # stdin não é de escrita
        with self.assertRaises(ErroFD):
            self.pai.ler(1, 1)
        with self.assertRaises(FileNotFoundError):
            self.pai.abrir("nada", "r")
        with self.assertRaises(ValueError):
            self.pai.abrir("f", "z")

    def test_stdin_e_stdout_do_console(self):
        self.sis.stdin += b"teclado"
        self.assertEqual(self.pai.ler(0, 3), b"tec")
        self.pai.escrever(1, b"tela")
        self.pai.escrever(2, b"erro")
        self.assertEqual((bytes(self.sis.stdout), bytes(self.sis.stderr)), (b"tela", b"erro"))


if __name__ == "__main__":
    unittest.main()
