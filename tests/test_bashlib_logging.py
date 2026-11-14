import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "logging.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


def com_env(**kw):
    env = {k: v for k, v in os.environ.items() if k not in ("NO_COLOR", "LOG_COLOR", "LOG_LEVEL")}
    env.update(kw)
    return env


class TestLogging(unittest.TestCase):
    def test_info_padrao(self):
        r = executar("info", "ola", "mundo", env=com_env())
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stderr, "[INFO] ola mundo\n")

    def test_debug_filtrado_por_nivel(self):
        r = executar("debug", "x", env=com_env())
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        r = executar("debug", "x", env=com_env(LOG_LEVEL="debug"))
        self.assertEqual(r.stderr, "[DEBUG] x\n")

    def test_nivel_error_descarta_warn(self):
        env = com_env(LOG_LEVEL="error")
        self.assertEqual(executar("warn", "x", env=env).stderr, "")
        self.assertEqual(executar("error", "falhou", env=env).stderr, "[ERROR] falhou\n")

    def test_cor_forcada_e_desligada(self):
        r = executar("warn", "x", env=com_env(LOG_COLOR="1"))
        self.assertIn("\x1b[33m", r.stderr)
        r = executar("warn", "x", env=com_env(LOG_COLOR="1", NO_COLOR="1"))
        self.assertNotIn("\x1b", r.stderr)
        r = executar("warn", "x", env=com_env(LOG_COLOR="0"))
        self.assertNotIn("\x1b", r.stderr)

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; log_warn aviso; log_info ok'],
                           capture_output=True, text=True, env=com_env())
        self.assertEqual(r.stderr, "[WARN] aviso\n[INFO] ok\n")

    def test_help(self):
        r = executar("--help", env=com_env())
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar(env=com_env()).returncode, 2)
        self.assertEqual(executar("fatal", "x", env=com_env()).returncode, 2)
        self.assertEqual(executar("info", env=com_env()).returncode, 2)
        self.assertEqual(executar("info", "x", env=com_env(LOG_LEVEL="zzz")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
