import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'tabuada.awk'
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


class TestTabuada(unittest.TestCase):
    def test_normal(self):
        r = executar(['-v', 'n=3', '-v', 'ate=3'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '3 x 1 = 3\n3 x 2 = 6\n3 x 3 = 9\n')

    def test_padrao_ate_10(self):
        r = executar(['-v', 'n=7'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        linhas = r.stdout.splitlines()
        self.assertEqual(len(linhas), 10)
        self.assertEqual(linhas[0], '7 x 1 = 7')
        self.assertEqual(linhas[-1], '7 x 10 = 70')

    def test_zero(self):
        r = executar(['-v', 'n=0', '-v', 'ate=0'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_n_invalido(self):
        r = executar(['-v', 'n=x'], [], '', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('erro', r.stderr)

    def test_sem_n(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('erro', r.stderr)


if __name__ == "__main__":
    unittest.main()
