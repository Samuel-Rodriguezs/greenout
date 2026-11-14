import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'valida_cpf.awk'
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


class TestValidaCpf(unittest.TestCase):
    def test_normal(self):
        r = executar([], [], '123.456.789-09\n12345678909\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '123.456.789-09\tVALIDO\n12345678909\tVALIDO\n')

    def test_invalidos(self):
        r = executar([], [], '111.111.111-11\n123.456.789-0\nabc\n123.456.78909\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '111.111.111-11\tINVALIDO\n123.456.789-0\tINVALIDO\nabc\tINVALIDO\n123.456.78909\tINVALIDO\n')

    def test_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_linhas_em_branco(self):
        r = executar([], [], '\n   \n\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')


if __name__ == "__main__":
    unittest.main()
