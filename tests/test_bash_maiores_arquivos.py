import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "maiores_arquivos.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestMaioresArquivos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / "sub").mkdir()
        (self.dir / "pequeno.txt").write_bytes(b"x" * 10)
        (self.dir / "medio.txt").write_bytes(b"x" * 100)
        (self.dir / "sub" / "grande.bin").write_bytes(b"x" * 1000)
        (self.dir / "sub" / "enorme.bin").write_bytes(b"x" * 5000)

    def linhas(self, r):
        return r.stdout.splitlines()

    def test_padrao_lista_todos_ordenados(self):
        r = executar(str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        tamanhos = [int(l.split()[0]) for l in self.linhas(r)]
        self.assertEqual(tamanhos, [5000, 1000, 100, 10])
        self.assertTrue(self.linhas(r)[0].endswith("enorme.bin"))

    def test_limita_com_n(self):
        r = executar("-n", "2", str(self.dir))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.linhas(r)), 2)
        self.assertTrue(self.linhas(r)[1].endswith("grande.bin"))

    def test_diretorio_vazio(self):
        vazio = self.dir / "vazio"
        vazio.mkdir()
        r = executar(str(vazio))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_diretorio_inexistente(self):
        r = executar(str(self.dir / "nao_existe"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("nao encontrado", r.stderr)

    def test_n_invalido(self):
        for valor in ("abc", "0", "-3"):
            r = executar("-n", valor, str(self.dir))
            self.assertEqual(r.returncode, 2, valor)

    def test_help_e_sem_argumentos(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)
        self.assertEqual(executar().returncode, 2)


if __name__ == "__main__":
    unittest.main()
