import re
import subprocess
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "tempo_execucao.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestTempoExecucao(unittest.TestCase):
    def test_mede_tempo(self):
        r = executar("sleep", "0.2")
        self.assertEqual(r.returncode, 0, r.stderr)
        m = re.search(r"tempo: (\d+)\.(\d{3}) s \(saida=0\)", r.stderr)
        self.assertIsNotNone(m, r.stderr)
        ms = int(m.group(1)) * 1000 + int(m.group(2))
        self.assertGreaterEqual(ms, 190)
        self.assertLess(ms, 3000)

    def test_preserva_stdout(self):
        r = executar("echo", "ola")
        self.assertEqual(r.stdout, "ola\n")

    def test_propaga_codigo_de_saida(self):
        r = executar("bash", "-c", "exit 7")
        self.assertEqual(r.returncode, 7)
        self.assertIn("saida=7", r.stderr)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_comando_inexistente(self):
        self.assertEqual(executar("comando_que_nao_existe_xyz").returncode, 127)

    def test_sem_argumento(self):
        self.assertEqual(executar().returncode, 1)


if __name__ == "__main__":
    unittest.main()
