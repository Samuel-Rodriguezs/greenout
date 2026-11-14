import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_notas import main


class TestCliNotas(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.arq = str(Path(self.dir.name) / "n.json")

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["--arquivo", self.arq, *args])
        return code, buf.getvalue().strip()

    def test_nova_e_listar(self):
        self.assertEqual(self.rodar("nova", "comprar pão", "--tags", "casa", "mercado"), (0, "nota 1 salva"))
        self.assertEqual(self.rodar("listar"), (0, "1: comprar pão #casa #mercado"))

    def test_filtro_tag(self):
        self.rodar("nova", "a", "--tags", "x")
        self.rodar("nova", "b", "--tags", "y")
        self.assertEqual(self.rodar("listar", "--tag", "y"), (0, "2: b #y"))

    def test_buscar(self):
        self.rodar("nova", "Reunião às 10h")
        self.assertEqual(self.rodar("buscar", "reunião")[0], 0)
        self.assertEqual(self.rodar("buscar", "zzz"), (1, ""))


if __name__ == "__main__":
    unittest.main()
