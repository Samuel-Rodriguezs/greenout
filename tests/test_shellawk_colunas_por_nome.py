import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'colunas_por_nome.awk'
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


class TestColunasPorNome(unittest.TestCase):
    def test_normal(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'cols=idade,nome'], [], 'nome,idade,cidade\nAna,30,SP\nBia,25,RJ\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'idade,nome\n30,Ana\n25,Bia\n')

    def test_coluna_inexistente(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'cols=foo'], [], 'nome,idade\nAna,30\n', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('coluna inexistente: foo', r.stderr)

    def test_vazia(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'cols=a'], [], '', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_linha_curta(self):
        r = executar(['-F,', '-v', 'OFS=,', '-v', 'cols=idade'], [], 'nome,idade\nAna,30\nBia\n', {})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'idade\n30\n\n')

    def test_sem_cols(self):
        r = executar([], [], 'a\n1\n', {})
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('informe', r.stderr)


if __name__ == "__main__":
    unittest.main()
