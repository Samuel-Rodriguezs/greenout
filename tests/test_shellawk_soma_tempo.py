import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'soma_tempo.awk'
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


class TestSomaTempo(unittest.TestCase):
    def test_normal(self):
        r = executar([], [], '01:30:00\n00:45:30\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '02:15:30\n')

    def test_vai_um(self):
        r = executar([], [], '00:59:59\n00:00:01\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '01:00:00\n')

    def test_horas_grandes(self):
        r = executar([], [], '99:59:59\n00:00:01\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '100:00:00\n')

    def test_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '00:00:00\n')

    def test_malformadas(self):
        r = executar([], [], '1:2\n99:61:00\nabc\n00:00:10\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '00:00:10\n')
        self.assertIn('ignorada: abc', r.stderr)


if __name__ == "__main__":
    unittest.main()
