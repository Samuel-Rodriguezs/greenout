import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'data_br_iso.sed'
TIPO = 'sed'


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


class TestDataBrIso(unittest.TestCase):
    def test_normal(self):
        r = executar(['-E'], [], 'Nasc: 25/12/1999.\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'Nasc: 1999-12-25.\n')

    def test_varias_na_linha(self):
        r = executar(['-E'], [], '01/02/2020 e 31/12/2021\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '2020-02-01 e 2021-12-31\n')

    def test_vazia(self):
        r = executar(['-E'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_malformadas(self):
        r = executar(['-E'], [], '32/13/2020 e 5/5/2020 e 2020-01-01\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '32/13/2020 e 5/5/2020 e 2020-01-01\n')


if __name__ == "__main__":
    unittest.main()
