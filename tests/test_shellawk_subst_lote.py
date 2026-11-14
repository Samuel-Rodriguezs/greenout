import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'subst_lote.sh'
TIPO = 'sh'


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


class TestSubstLote(unittest.TestCase):
    def test_backreferences(self):
        r = executar([], ['{d}/r.tsv'], 'abc-123 e xy-9\n', {'r.tsv': '([a-z]+)-([0-9]+)\t\\2:\\1\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '123:abc e 9:xy\n')

    def test_regras_em_ordem_e_comentarios(self):
        r = executar([], ['{d}/r.tsv'], 'a-b\n', {'r.tsv': '# comentario\n\na\tZ\nZ-b\tZ-b\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'Z-b\n')

    def test_entrada_vazia(self):
        r = executar([], ['{d}/r.tsv'], '', {'r.tsv': 'x\ty\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_regra_malformada(self):
        r = executar([], ['{d}/r.tsv'], 'x\n', {'r.tsv': 'semtab\nx\tY\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, 'Y\n')
        self.assertIn('regra malformada na linha 1', r.stderr)

    def test_regras_inexistentes(self):
        r = executar([], ['{d}/nao_existe.tsv'], 'x\n', {})
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertEqual(r.stdout, '')
        self.assertIn('uso:', r.stderr)


if __name__ == "__main__":
    unittest.main()
