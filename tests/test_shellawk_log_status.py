import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'log_status.awk'
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


class TestLogStatus(unittest.TestCase):
    def test_normal(self):
        r = executar([], [], '1.1.1.1 - - [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 512\n1.1.1.2 - - [10/Oct/2023:13:55:37 +0000] "GET /x HTTP/1.1" 404 10\n1.1.1.1 - - [10/Oct/2023:13:55:38 +0000] "POST /a HTTP/1.1" 200 7\n1.1.1.3 - - [10/Oct/2023:13:55:39 +0000] "GET /b HTTP/1.1" 500 0\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '200 2\n404 1\n500 1\n')

    def test_vazia(self):
        r = executar([], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_malformadas(self):
        r = executar([], [], 'lixo\n\n1.1.1.1 - - [d] "GET / HTTP/1.1" 200 5\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '200 1\n')
        self.assertIn('malformadas: 2', r.stderr)


if __name__ == "__main__":
    unittest.main()
