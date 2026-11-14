import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'juntar_linhas.awk'
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


class TestJuntarLinhas(unittest.TestCase):
    def test_normal(self):
        r = executar(['-v', 'n=3'], [], 'a\nb\nc\nd\ne\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a,b,c\nd,e\n')

    def test_separador(self):
        r = executar(['-v', 'n=2', '-v', 'sep=;'], [], 'a\nb\nc\nd\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a;b\nc;d\n')

    def test_vazia(self):
        r = executar(['-v', 'n=3'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_n_um(self):
        r = executar(['-v', 'n=1'], [], 'a\n\nb\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a\n\nb\n')

    def test_n_invalido(self):
        r = executar(['-v', 'n=0'], [], 'a\n', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('n invalido', r.stderr)


if __name__ == "__main__":
    unittest.main()
