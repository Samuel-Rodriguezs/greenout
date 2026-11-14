import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "extrair_urls.sh"


def executar(*args, entrada=None):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True,
                          text=True, input=entrada)


class TestExtrairUrls(unittest.TestCase):
    def test_arquivo(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "t.txt"
            arq.write_text("Veja https://exemplo.com/a?x=1, e também http://outro.org.\nfim\n")
            r = executar(str(arq))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(r.stdout.splitlines(),
                             ["https://exemplo.com/a?x=1", "http://outro.org"])

    def test_stdin_unicas(self):
        r = executar("-u", entrada="http://a.com http://b.com http://a.com\n")
        self.assertEqual(r.stdout.splitlines(), ["http://a.com", "http://b.com"])

    def test_sem_urls(self):
        r = executar(entrada="nada aqui\n")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_arquivo_inexistente(self):
        self.assertEqual(executar("/nao/existe.txt").returncode, 2)

    def test_opcao_invalida(self):
        self.assertNotEqual(executar("-z").returncode, 0)


if __name__ == "__main__":
    unittest.main()
