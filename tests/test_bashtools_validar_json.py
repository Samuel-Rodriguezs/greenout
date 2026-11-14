import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-tools" / "validar_json.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestValidarJson(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_json_valido(self):
        arq = self.dir / "ok.json"
        arq.write_text('{"a": [1, 2, 3]}')
        r = executar(str(arq))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ok:", r.stdout)

    def test_json_invalido(self):
        arq = self.dir / "ruim.json"
        arq.write_text('{"a": ')
        r = executar(str(arq))
        self.assertEqual(r.returncode, 3)
        self.assertIn("invalido:", r.stdout)

    def test_varios_arquivos_um_invalido(self):
        bom = self.dir / "bom.json"
        bom.write_text("[]")
        ruim = self.dir / "ruim.json"
        ruim.write_text("{")
        r = executar(str(bom), str(ruim))
        self.assertEqual(r.returncode, 3)
        self.assertIn("ok:", r.stdout)

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_arquivo_inexistente(self):
        self.assertEqual(executar(str(self.dir / "x.json")).returncode, 2)

    def test_sem_argumento(self):
        self.assertNotEqual(executar().returncode, 0)


if __name__ == "__main__":
    unittest.main()
