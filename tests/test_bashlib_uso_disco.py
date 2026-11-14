import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "uso_disco.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestUsoDisco(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        (self.raiz / "grande").mkdir()
        (self.raiz / "grande" / "f").write_bytes(b"x" * 3000)
        (self.raiz / "pequeno").mkdir()
        (self.raiz / "pequeno" / "f").write_bytes(b"x" * 500)
        (self.raiz / "solto.txt").write_bytes(b"x" * 500)

    def linhas(self, r):
        return [re.split(r"\s+", l.strip(), maxsplit=2) for l in r.stdout.splitlines()]

    def test_bytes_e_ordem(self):
        r = executar("-b", str(self.raiz))
        self.assertEqual(r.returncode, 0, r.stderr)
        l = self.linhas(r)
        self.assertEqual([x[2] for x in l], ["grande/", "(arquivos soltos)", "pequeno/", "TOTAL"])
        self.assertEqual([x[0] for x in l], ["3000", "500", "500", "4000"])
        self.assertEqual(l[0][1], "75.0%")
        self.assertEqual(l[-1][1], "100.0%")

    def test_top(self):
        r = executar("-b", "-n", "1", str(self.raiz))
        nomes = [x[2] for x in self.linhas(r)]
        self.assertEqual(nomes, ["grande/", "TOTAL"])

    def test_humano(self):
        (self.raiz / "grande" / "g").write_bytes(b"x" * 2000)
        r = executar(str(self.raiz))
        self.assertIn("4.9K", r.stdout)

    def test_dir_vazio(self):
        with tempfile.TemporaryDirectory() as d:
            r = executar("-b", d)
            self.assertEqual(r.returncode, 0)
            self.assertIn("TOTAL", r.stdout)

    def test_help(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("/nao/existe").returncode, 2)
        self.assertEqual(executar("-n", "x", str(self.raiz)).returncode, 2)
        self.assertEqual(executar("-z", str(self.raiz)).returncode, 2)


if __name__ == "__main__":
    unittest.main()
