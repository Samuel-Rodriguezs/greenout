import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_todo import main


class TestCliTodo(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.arq = str(Path(self.dir.name) / "t.json")

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["--arquivo", self.arq, *args])
        return code, buf.getvalue().strip()

    def test_add_list(self):
        self.rodar("add", "estudar")
        self.rodar("add", "treinar")
        _, out = self.rodar("list")
        self.assertEqual(out, "1. [ ] estudar\n2. [ ] treinar")

    def test_done_e_pendentes(self):
        self.rodar("add", "a")
        self.rodar("add", "b")
        self.assertEqual(self.rodar("done", "1")[0], 0)
        _, out = self.rodar("list", "--pendentes")
        self.assertEqual(out, "2. [ ] b")
        self.assertTrue(json.loads(Path(self.arq).read_text())[0]["feita"])

    def test_rm_e_ids_nao_reutilizados(self):
        self.rodar("add", "a")
        self.rodar("add", "b")
        self.rodar("rm", "2")
        self.assertIn("tarefa 2 adicionada", self.rodar("add", "c")[1])

    def test_inexistente(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.rodar("done", "9")[0], 1)


if __name__ == "__main__":
    unittest.main()
