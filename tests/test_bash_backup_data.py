import os
import re
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "backup_data.sh"


def executar(*args, env_extra=None):
    env = dict(os.environ)
    env.pop("BACKUP_DATA", None)
    env.update(env_extra or {})
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True,
                          text=True, env=env)


class TestBackupData(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_backup_com_data_fixa(self):
        origem = self.dir / "dados.csv"
        origem.write_text("a,b\n1,2\n")
        destino = self.dir / "bkp" / "sub"
        r = executar(str(origem), str(destino), env_extra={"BACKUP_DATA": "2024-03-09"})
        self.assertEqual(r.returncode, 0, r.stderr)
        esperado = destino / "dados_2024-03-09.csv"
        self.assertEqual(r.stdout.strip(), str(esperado))
        self.assertEqual(esperado.read_text(), "a,b\n1,2\n")
        self.assertTrue(origem.exists())

    def test_sem_extensao(self):
        origem = self.dir / "LEIAME"
        origem.write_text("x")
        r = executar(str(origem), str(self.dir / "b"), env_extra={"BACKUP_DATA": "2024-01-02"})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.dir / "b" / "LEIAME_2024-01-02").is_file())

    def test_data_padrao_e_hoje(self):
        origem = self.dir / "n.txt"
        origem.write_text("x")
        r = executar(str(origem), str(self.dir / "b"))
        self.assertEqual(r.returncode, 0, r.stderr)
        nome = Path(r.stdout.strip()).name
        self.assertRegex(nome, r"^n_\d{4}-\d{2}-\d{2}\.txt$")
        data = re.search(r"\d{4}-\d{2}-\d{2}", nome).group(0)
        # tolera virada de meia-noite durante o teste
        delta = abs((date.today() - date.fromisoformat(data)).days)
        self.assertLessEqual(delta, 1)

    def test_data_invalida(self):
        origem = self.dir / "n.txt"
        origem.write_text("x")
        r = executar(str(origem), str(self.dir / "b"), env_extra={"BACKUP_DATA": "ontem"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("invalida", r.stderr)

    def test_origem_inexistente(self):
        r = executar(str(self.dir / "nada"), str(self.dir / "b"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("nao encontrado", r.stderr)

    def test_argumentos_errados_e_help(self):
        self.assertEqual(executar().returncode, 2)
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)


if __name__ == "__main__":
    unittest.main()
