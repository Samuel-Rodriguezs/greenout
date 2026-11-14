import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_csv_json import main


class TestCliCsvJson(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.base = Path(self.dir.name)

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(list(args))
        return code, buf.getvalue()

    def test_csv_para_json(self):
        arq = self.base / "a.csv"
        arq.write_text("nome,idade\nAna,30\nJoão,25\n", encoding="utf-8")
        code, out = self.rodar(str(arq))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out), [{"nome": "Ana", "idade": "30"}, {"nome": "João", "idade": "25"}])

    def test_json_para_csv_arquivo(self):
        arq = self.base / "a.json"
        arq.write_text(json.dumps([{"a": 1, "b": 2}, {"a": 3, "c": 4}]), encoding="utf-8")
        saida = self.base / "o.csv"
        self.assertEqual(self.rodar(str(arq), "-o", str(saida))[0], 0)
        self.assertEqual(saida.read_text(encoding="utf-8"), "a,b,c\n1,2,\n3,,4\n")

    def test_delimitador(self):
        arq = self.base / "a.csv"
        arq.write_text("x;y\n1;2\n", encoding="utf-8")
        _, out = self.rodar(str(arq), "-d", ";")
        self.assertEqual(json.loads(out), [{"x": "1", "y": "2"}])

    def test_erros(self):
        ruim = self.base / "r.json"
        ruim.write_text('{"a": 1}', encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.rodar(str(ruim))[0], 1)
            self.assertEqual(self.rodar(str(self.base / "nada.csv"))[0], 1)


if __name__ == "__main__":
    unittest.main()
