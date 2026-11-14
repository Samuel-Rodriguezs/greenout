import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "monitor_tamanho.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestMonitorTamanho(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        (self.dir / "grande.bin").write_bytes(b"x" * 5000)  # 5 KB arredondado

    def test_dentro_do_limite(self):
        r = executar(str(self.dir), "10")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok:", r.stdout)
        self.assertIn("5 KB", r.stdout)

    def test_limite_excedido(self):
        r = executar(str(self.dir), "2")
        self.assertEqual(r.returncode, 3)
        self.assertIn("ALERTA", r.stdout)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_pasta_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x"), "5").returncode, 2)

    def test_limite_invalido(self):
        self.assertEqual(executar(str(self.dir), "abc").returncode, 1)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()
