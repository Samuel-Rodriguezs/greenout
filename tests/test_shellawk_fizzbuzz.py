import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'fizzbuzz.awk'
TIPO = 'awk'


def executar(opts=(), ops=(), entrada="", arquivos=None):
    with tempfile.TemporaryDirectory() as d:
        for nome, conteudo in (arquivos or {}).items():
            (Path(d) / nome).write_text(conteudo)
        ops = [o.format(d=d) for o in ops]
        if TIPO == "sh":
            cmd = ["sh", str(SCRIPT), *opts, *ops]
        else:
            cmd = [TIPO, *opts, "-f", str(SCRIPT), *ops]
        return subprocess.run(cmd, input=entrada, capture_output=True, text=True, timeout=30)


class TestFizzbuzz(unittest.TestCase):
    def test_ate_15(self):
        r = executar(['-v', 'n=15'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz\n')

    def test_zero(self):
        r = executar(['-v', 'n=0'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_padrao_100_linhas(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(len(linhas), 100)
        self.assertEqual(linhas[-1], 'Buzz')
        self.assertEqual(linhas[14], 'FizzBuzz')

    def test_n_invalido(self):
        r = executar(['-v', 'n=abc'], [], '', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('n invalido', r.stderr)


if __name__ == "__main__":
    unittest.main()
