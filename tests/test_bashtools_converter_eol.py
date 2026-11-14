import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "converter_eol.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestConverterEol(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.arq = Path(self.tmp.name) / "t.txt"

    def test_para_lf(self):
        self.arq.write_bytes(b"a\r\nb\r\n")
        r = executar("para-lf", str(self.arq))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.arq.read_bytes(), b"a\nb\n")

    def test_para_crlf(self):
        self.arq.write_bytes(b"a\nb\n")
        r = executar("para-crlf", str(self.arq))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.arq.read_bytes(), b"a\r\nb\r\n")

    def test_crlf_nao_duplica(self):
        self.arq.write_bytes(b"a\r\nb\n")
        executar("para-crlf", str(self.arq))
        self.assertEqual(self.arq.read_bytes(), b"a\r\nb\r\n")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_modo_invalido(self):
        self.arq.write_text("x")
        self.assertEqual(executar("xpto", str(self.arq)).returncode, 1)

    def test_arquivo_inexistente(self):
        self.assertEqual(executar("para-lf", str(self.arq)).returncode, 2)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()
