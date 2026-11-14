import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'histograma.awk'
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


class TestHistograma(unittest.TestCase):
    def test_normal(self):
        r = executar(['-v', 'largura=10'], [], 'a 10\nbb 5\nc 0\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a  | ########## 10\nbb | ##### 5\nc  |  0\n')

    def test_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_malformadas(self):
        r = executar(['-v', 'largura=2'], [], 'x\ny abc\nz -3\nw 1 2\nok 1\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'ok | ## 1\n')


if __name__ == "__main__":
    unittest.main()
