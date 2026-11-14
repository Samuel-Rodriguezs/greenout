import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_prototype import Documento, RegistroModelos


class TestPrototype(unittest.TestCase):
    def test_copia_profunda(self):
        a = Documento("Ata", ["abertura"], {"autor": "x"})
        b = a.clonar()
        b.secoes.append("encerramento")
        b.metadados["autor"] = "y"
        self.assertEqual(a.secoes, ["abertura"])
        self.assertEqual(a.metadados["autor"], "x")

    def test_alteracoes(self):
        b = Documento("Ata").clonar(titulo="Ata 2")
        self.assertEqual(b.titulo, "Ata 2")
        with self.assertRaises(AttributeError):
            Documento("Ata").clonar(inexistente=1)

    def test_registro_isola_modelo(self):
        reg = RegistroModelos()
        m = Documento("Contrato", ["objeto"])
        reg.registrar("c", m)
        m.secoes.append("alterado")
        d = reg.criar("c", titulo="Contrato X")
        self.assertEqual(d.secoes, ["objeto"])
        d.secoes.append("foro")
        self.assertEqual(reg.criar("c").secoes, ["objeto"])


if __name__ == "__main__":
    unittest.main()
