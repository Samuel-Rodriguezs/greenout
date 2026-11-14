import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash" / "resumo_log.sh"


def executar(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


class TestResumoLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def log(self, conteudo):
        p = self.dir / "app.log"
        p.write_text(conteudo, encoding="utf-8")
        return str(p)

    def test_conta_niveis(self):
        r = executar(self.log(
            "2024-01-01 INFO iniciando\n"
            "2024-01-01 WARN disco quase cheio\n"
            "2024-01-01 ERROR falha ao conectar\n"
            "2024-01-01 INFO conectado\n"
            "2024-01-01 ERROR timeout\n"
            "2024-01-01 ERROR outra falha\n"
        ))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "ERROR: 3\nWARN: 1\nINFO: 2\n")

    def test_sem_ocorrencias_nao_aborta(self):
        r = executar(self.log("nada relevante\n"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "ERROR: 0\nWARN: 0\nINFO: 0\n")

    def test_palavra_inteira(self):
        r = executar(self.log("INFORMATION x\nERRORS y\nWARNING z\n"))
        self.assertEqual(r.stdout, "ERROR: 0\nWARN: 0\nINFO: 0\n")

    def test_arquivo_inexistente(self):
        r = executar(str(self.dir / "nao.log"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("nao encontrado", r.stderr)

    def test_help_e_sem_argumentos(self):
        r = executar("-h")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)
        self.assertEqual(executar().returncode, 2)


if __name__ == "__main__":
    unittest.main()
