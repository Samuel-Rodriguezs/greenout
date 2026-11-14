import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'extrair.awk'
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


class TestExtrair(unittest.TestCase):
    def test_emails(self):
        r = executar(['-v', 'tipo=email'], [], 'contato: ana@ex.com.br, b.c+d@foo.org!\nnada\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'ana@ex.com.br\nb.c+d@foo.org\n')

    def test_ips(self):
        r = executar(['-v', 'tipo=ip'], [], 'ip 10.0.0.1 e 999.1.1.1 e 192.168.1.255\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '10.0.0.1\n192.168.1.255\n')

    def test_vazia(self):
        r = executar(['-v', 'tipo=ip'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_emails_malformados(self):
        r = executar(['-v', 'tipo=email'], [], '@@ x@ @y a@b\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_tipo_invalido(self):
        r = executar(['-v', 'tipo=cep'], [], 'x\n', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('tipo=email|ip', r.stderr)


if __name__ == "__main__":
    unittest.main()
