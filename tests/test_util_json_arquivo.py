import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from util_json_arquivo import escrever_json, ler_json


class TestJsonArquivo(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.dir = Path(self._dir.name)

    def test_ida_e_volta_com_acentos(self):
        dados = {"nome": "João", "itens": [1, 2.5, None, True]}
        arq = self.dir / "a.json"
        escrever_json(arq, dados)
        self.assertEqual(ler_json(arq), dados)
        self.assertIn("João", arq.read_text(encoding="utf-8"))

    def test_sobrescreve(self):
        arq = self.dir / "a.json"
        escrever_json(arq, {"v": 1})
        escrever_json(arq, {"v": 2})
        self.assertEqual(ler_json(arq), {"v": 2})

    def test_sem_arquivos_temporarios_sobrando(self):
        escrever_json(self.dir / "a.json", [1])
        self.assertEqual([p.name for p in self.dir.iterdir()], ["a.json"])

    def test_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            ler_json(self.dir / "nao.json")

    def test_json_invalido(self):
        arq = self.dir / "ruim.json"
        arq.write_text("{quebrado", encoding="utf-8")
        with self.assertRaises(ValueError):
            ler_json(arq)

    def test_dado_nao_serializavel_nao_corrompe(self):
        arq = self.dir / "a.json"
        escrever_json(arq, {"ok": 1})
        with self.assertRaises(TypeError):
            escrever_json(arq, {"x": object()})
        self.assertEqual(ler_json(arq), {"ok": 1})
        self.assertEqual([p.name for p in self.dir.iterdir()], ["a.json"])


if __name__ == "__main__":
    unittest.main()
