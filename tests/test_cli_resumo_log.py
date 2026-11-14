import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_resumo_log import main, resumir

LOG = """2024-01-01 10:00 INFO: iniciado
2024-01-01 10:01 ERROR: falha de conexão
2024-01-01 10:02 WARN: lento
2024-01-01 10:03 ERROR: falha de conexão
2024-01-01 10:04 ERROR: disco cheio
linha sem nível
"""


class TestCliResumoLog(unittest.TestCase):
    def test_resumir(self):
        niveis, erros = resumir(LOG.splitlines())
        self.assertEqual(niveis, {"INFO": 1, "ERROR": 3, "WARNING": 1})
        self.assertEqual(erros["falha de conexão"], 2)

    def test_main(self):
        with tempfile.TemporaryDirectory() as d:
            arq = Path(d) / "a.log"
            arq.write_text(LOG, encoding="utf-8")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = main([str(arq), "--top", "1"])
        self.assertEqual(code, 0)
        linhas = buf.getvalue().splitlines()
        self.assertEqual(linhas[:3], ["INFO: 1", "WARNING: 1", "ERROR: 3"])
        self.assertEqual(linhas[-1], "  2x falha de conexão")
        self.assertEqual(len(linhas), 5)

    def test_arquivo_inexistente(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["/nao/existe.log"]), 1)


if __name__ == "__main__":
    unittest.main()
