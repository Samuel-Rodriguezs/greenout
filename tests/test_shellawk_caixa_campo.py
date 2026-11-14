import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'caixa_campo.awk'
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


class TestCaixaCampo(unittest.TestCase):
    def test_upper(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'campo=2', '-v', 'modo=upper'], [], 'a,bc,d\nx,yz\nsolo\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a,BC,d\nx,YZ\nsolo\n')

    def test_lower(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'campo=2', '-v', 'modo=lower'], [], 'A,BC\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'A,bc\n')

    def test_title(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'campo=2', '-v', 'modo=title'], [], '1,maria da SILVA\n2,ANA-LU\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1,Maria Da Silva\n2,Ana-Lu\n')

    def test_vazia(self):
        r = executar(['-v', 'campo=1', '-v', 'modo=upper'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_modo_invalido(self):
        r = executar(['-v', 'campo=1', '-v', 'modo=x'], [], 'a\n', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('modo=upper|lower|title', r.stderr)


if __name__ == "__main__":
    unittest.main()
