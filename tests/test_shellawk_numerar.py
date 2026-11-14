import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'numerar.awk'
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


class TestNumerar(unittest.TestCase):
    def test_normal(self):
        r = executar([], [], 'a\nb\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1\ta\n2\tb\n')

    def test_inicio(self):
        r = executar(['-v', 'inicio=10'], [], 'a\nb\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '10\ta\n11\tb\n')

    def test_pular_vazias(self):
        r = executar(['-v', 'pular_vazias=1'], [], 'a\n\nb\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1\ta\n\n2\tb\n')

    def test_vazia_numerada(self):
        r = executar([], [], 'a\n\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1\ta\n2\t\n')

    def test_entrada_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')


if __name__ == "__main__":
    unittest.main()
