import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'tabela.awk'
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


class TestTabela(unittest.TestCase):
    def test_normal(self):
        r = executar(['-F,'], [], 'nome,idade\nAna,3\nCarolina,45\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'nome     | idade\n---------+------\nAna      | 3\nCarolina | 45\n')

    def test_irregular(self):
        r = executar(['-F,'], [], 'a,b\nc\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'a | b\n--+--\nc |\n')

    def test_vazia(self):
        r = executar(['-F,'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')


if __name__ == "__main__":
    unittest.main()
