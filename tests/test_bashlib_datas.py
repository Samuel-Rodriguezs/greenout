import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "datas.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestDatas(unittest.TestCase):
    def test_diff(self):
        self.assertEqual(executar("diff", "2024-01-01", "2024-03-01").stdout, "60\n")
        self.assertEqual(executar("diff", "2024-03-01", "2024-01-01").stdout, "-60\n")
        self.assertEqual(executar("diff", "2023-01-01", "2024-01-01").stdout, "365\n")

    def test_dia_semana(self):
        self.assertEqual(executar("dia_semana", "2024-01-01").stdout, "segunda-feira\n")
        self.assertEqual(executar("dia_semana", "2000-01-01").stdout, "sabado\n")
        self.assertEqual(executar("dia_semana", "2023-12-31").stdout, "domingo\n")

    def test_somar(self):
        self.assertEqual(executar("somar", "2024-02-28", "2").stdout, "2024-03-01\n")
        self.assertEqual(executar("somar", "2024-01-01", "-1").stdout, "2023-12-31\n")

    def test_bissexto(self):
        self.assertEqual(executar("bissexto", "2024").returncode, 0)
        self.assertEqual(executar("bissexto", "1900").returncode, 1)
        self.assertEqual(executar("bissexto", "2000").stdout, "sim\n")

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; dat_diff 2024-01-01 2024-01-11'],
                           capture_output=True, text=True)
        self.assertEqual(r.stdout, "10\n")

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("x").returncode, 2)
        self.assertEqual(executar("diff", "2024-02-30", "2024-03-01").returncode, 1)
        self.assertEqual(executar("dia_semana", "ontem").returncode, 1)
        self.assertEqual(executar("somar", "2024-01-01", "abc").returncode, 2)
        self.assertEqual(executar("diff", "2024-01-01").returncode, 2)


if __name__ == "__main__":
    unittest.main()
