import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "shell-awk" / 'join.awk'
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


class TestJoin(unittest.TestCase):
    def test_normal(self):
        r = executar(['-F,'], ['{d}/a.csv', '{d}/b.csv'], '', {'a.csv': '1,ana\n2,bia\n3,caio\n', 'b.csv': '2,10,x\n3,20,y\n9,30,z\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '2,bia,10,x\n3,caio,20,y\n')

    def test_esquerda_vazia(self):
        r = executar(['-F,'], ['{d}/a.csv', '{d}/b.csv'], '', {'a.csv': '', 'b.csv': '1,x\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_ambas_vazias(self):
        r = executar(['-F,'], ['{d}/a.csv', '{d}/b.csv'], '', {'a.csv': '', 'b.csv': ''})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '')

    def test_malformadas(self):
        r = executar(['-F,'], ['{d}/a.csv', '{d}/b.csv'], '', {'a.csv': '\n,sem_chave\n1,a\nlixo\n', 'b.csv': '\n,z\n1,b\n'})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, '1,a,b\n')


if __name__ == "__main__":
    unittest.main()
