import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'estat_coluna.awk'
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


class TestEstatColuna(unittest.TestCase):
    def test_normal(self):
        r = executar(['-F,', '-v', 'col=2'], [], 'nome,v\na,10\nb,20\nc,troca\nd,30\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'n=3 soma=60 media=20 min=10 max=30\n')

    def test_decimais(self):
        r = executar([], [], '1.5\n2.5\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'n=2 soma=4 media=2 min=1.5 max=2.5\n')

    def test_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'n=0 soma=0 media=0 min=0 max=0\n')

    def test_malformadas(self):
        r = executar(['-F,', '-v', 'col=2'], [], 'x\n\n,\nabc,def\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'n=0 soma=0 media=0 min=0 max=0\n')


if __name__ == "__main__":
    unittest.main()
