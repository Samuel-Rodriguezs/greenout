import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'soma_por_chave.awk'
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


class TestSomaPorChave(unittest.TestCase):
    def test_normal(self):
        r = executar(['-F,'], [], 'a,1\nb,2\na,3.5\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a,4.5,2\nb,2,1\n')

    def test_colunas_customizadas(self):
        r = executar(['-F,', '-v', 'k=2', '-v', 'v=3'], [], '1,x,10\n2,x,20\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'x,30,2\n')

    def test_vazia(self):
        r = executar(['-F,'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_malformadas(self):
        r = executar(['-F,'], [], 'a,4\nc,x\n,5\nsolta\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a,4,1\n')


if __name__ == "__main__":
    unittest.main()
