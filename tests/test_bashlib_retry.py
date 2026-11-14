import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "retry.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


def env_sleep():
    env = dict(os.environ)
    env["RETRY_SLEEP"] = "echo"
    return env


class TestRetry(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.contador = Path(self.tmp.name) / "c"
        self.contador.write_text("0")
        # falha ate a tentativa N (argumento 2), depois sucesso
        self.script = Path(self.tmp.name) / "flaky.sh"
        self.script.write_text(
            'c=$(cat "$1"); c=$((c+1)); echo $c > "$1"; [ "$c" -ge "$2" ] && echo ok && exit 0; exit 3\n')

    def test_sucesso_imediato(self):
        r = executar("true", env=env_sleep())
        self.assertEqual((r.returncode, r.stdout), (0, ""))

    def test_sucesso_apos_falhas_com_backoff(self):
        r = executar("-d", "2", "bash", str(self.script), str(self.contador), "3", env=env_sleep())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.split(), ["2", "4", "ok"])
        self.assertEqual(self.contador.read_text().strip(), "3")

    def test_esgota_tentativas_e_propaga_codigo(self):
        r = executar("-n", "3", "bash", str(self.script), str(self.contador), "99", env=env_sleep())
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout.split(), ["1", "2"])
        self.assertIn("esgotadas 3 tentativas", r.stderr)

    def test_teto_do_atraso(self):
        r = executar("-n", "4", "-d", "5", "-m", "6", "false", env=env_sleep())
        self.assertEqual(r.stdout.split(), ["5", "6", "6"])

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("-n", "0", "true").returncode, 2)
        self.assertEqual(executar("-n", "x", "true").returncode, 2)
        self.assertEqual(executar("-q", "true").returncode, 2)


if __name__ == "__main__":
    unittest.main()
