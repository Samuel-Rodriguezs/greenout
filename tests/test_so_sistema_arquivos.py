import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_sistema_arquivos import (
    ArquivoGrande,
    DiretorioNaoVazio,
    EhDiretorio,
    JaExiste,
    NaoEhDiretorio,
    NaoEncontrado,
    SemEspaco,
    SistemaArquivos,
)


class TestSistemaArquivos(unittest.TestCase):
    def setUp(self):
        self.fs = SistemaArquivos(nblocos=12, tam_bloco=16)

    def test_diretorios_e_caminhos(self):
        fs = self.fs
        fs.mkdir("/home")
        fs.mkdir("/home/ana")
        fs.escrever("/home/ana/nota.txt", b"ola")
        self.assertEqual(fs.listar("/"), ["home"])
        self.assertEqual(fs.listar("/home/ana"), ["nota.txt"])
        fs.cd("/home/ana")
        self.assertEqual(fs.caminho_atual(), "/home/ana")
        self.assertEqual(fs.ler("nota.txt"), b"ola")
        self.assertEqual(fs.ler("../ana/./nota.txt"), b"ola")
        fs.cd("..")
        self.assertEqual(fs.caminho_atual(), "/home")
        fs.cd("../../..")  # .. na raiz permanece na raiz
        self.assertEqual(fs.caminho_atual(), "/")

    def test_caminho_relativo_a_partir_do_cwd(self):
        fs = self.fs
        fs.mkdir("/a")
        fs.cd("/a")
        fs.mkdir("b")
        fs.escrever("b/f", b"x")
        self.assertEqual(fs.ler("/a/b/f"), b"x")

    def test_blocos_diretos_apenas(self):
        fs = self.fs
        fs.escrever("/f", b"x" * 20)  # 2 blocos
        st = fs.stat("/f")
        self.assertEqual(len(st["diretos"]), 2)
        self.assertIsNone(st["indireto"])
        self.assertEqual(fs.livres(), 10)

    def test_bloco_indireto(self):
        fs = self.fs
        dados = bytes(range(70))  # 5 blocos de dados: 2 diretos + 3 via indireto
        fs.escrever("/g", dados)
        st = fs.stat("/g")
        self.assertEqual(len(st["diretos"]), 2)
        self.assertIsNotNone(st["indireto"])
        self.assertEqual(len(st["blocos"]), 5)
        self.assertEqual(fs.livres(), 12 - 5 - 1)  # +1 do bloco de ponteiros
        self.assertEqual(fs.ler("/g"), dados)

    def test_limite_de_tamanho(self):
        with self.assertRaises(ArquivoGrande):
            self.fs.escrever("/h", b"x" * 97)  # máximo (2+4)*16 = 96
        self.fs.escrever("/h", b"x" * 96)
        self.assertEqual(self.fs.livres(), 12 - 7)

    def test_sobrescrever_libera_blocos_antigos(self):
        fs = self.fs
        fs.escrever("/f", b"y" * 70)
        fs.escrever("/f", b"curto")
        self.assertEqual(fs.livres(), 11)
        self.assertEqual(fs.ler("/f"), b"curto")

    def test_disco_cheio_nao_corrompe(self):
        fs = self.fs
        fs.escrever("/a", b"a" * 96)  # 7 blocos
        with self.assertRaises(SemEspaco):
            fs.escrever("/b", b"b" * 96)  # precisa de 7, só há 5
        self.assertEqual(fs.livres(), 5)
        self.assertNotIn("b", fs.listar("/"))
        fs.escrever("/a", b"a" * 96)  # sobrescrever reaproveita os próprios blocos
        self.assertEqual(fs.ler("/a"), b"a" * 96)

    def test_hard_link_e_remocao(self):
        fs = self.fs
        fs.escrever("/f", b"dados")
        fs.link("/f", "/g")
        self.assertEqual(fs.stat("/g")["nlinks"], 2)
        self.assertEqual(fs.stat("/f")["inode"], fs.stat("/g")["inode"])
        fs.remover("/f")
        self.assertEqual(fs.ler("/g"), b"dados")
        self.assertEqual(fs.livres(), 11)
        fs.remover("/g")
        self.assertEqual(fs.livres(), 12)

    def test_remover_diretorio(self):
        fs = self.fs
        fs.mkdir("/d")
        fs.escrever("/d/f", b"1")
        with self.assertRaises(DiretorioNaoVazio):
            fs.remover("/d")
        fs.remover("/d/f")
        fs.remover("/d")
        self.assertEqual(fs.listar("/"), [])

    def test_erros(self):
        fs = self.fs
        fs.mkdir("/d")
        fs.escrever("/f", b"1")
        with self.assertRaises(JaExiste):
            fs.mkdir("/d")
        with self.assertRaises(NaoEncontrado):
            fs.ler("/nada")
        with self.assertRaises(EhDiretorio):
            fs.ler("/d")
        with self.assertRaises(EhDiretorio):
            fs.escrever("/d", b"x")
        with self.assertRaises(NaoEhDiretorio):
            fs.listar("/f")
        with self.assertRaises(NaoEhDiretorio):
            fs.escrever("/f/x", b"x")
        with self.assertRaises(EhDiretorio):
            fs.link("/d", "/l")


if __name__ == "__main__":
    unittest.main()
