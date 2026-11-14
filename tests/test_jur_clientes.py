import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from jur_clientes import CadastroClientes, TipoPessoa, criar_cliente

CPF = "529.982.247-25"
CNPJ = "11.222.333/0001-81"


class TestClientes(unittest.TestCase):
    def test_pf(self):
        c = criar_cliente(1, "  Maria   Silva ", "52998224725", "MARIA@X.com", "(11) 91234-5678")
        self.assertEqual(c.tipo, TipoPessoa.PF)
        self.assertEqual(c.documento, CPF)
        self.assertEqual(c.nome, "Maria Silva")
        self.assertEqual(c.email, "maria@x.com")
        self.assertEqual(c.telefone, "11912345678")

    def test_pj(self):
        c = criar_cliente(2, "Acme Ltda", CNPJ)
        self.assertEqual(c.tipo, TipoPessoa.PJ)
        self.assertEqual(c.documento, CNPJ)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            criar_cliente(1, "Fulano", "111.111.111-11")
        with self.assertRaises(ValueError):
            criar_cliente(1, "Fu", CPF)
        with self.assertRaises(ValueError):
            criar_cliente(1, "Fulano", CPF, email="sem-arroba")
        with self.assertRaises(ValueError):
            criar_cliente(1, "Fulano", CPF, telefone="123")

    def test_cadastro(self):
        cad = CadastroClientes()
        a = cad.cadastrar("Maria Silva", CPF)
        b = cad.cadastrar("Acme Ltda", CNPJ)
        self.assertEqual((a.id, b.id), (1, 2))
        self.assertEqual(len(cad), 2)
        with self.assertRaises(ValueError):
            cad.cadastrar("Outra Maria", "52998224725")
        self.assertEqual(cad.buscar_documento("11222333000181"), b)
        self.assertIsNone(cad.buscar_documento("00000000000"))
        self.assertEqual([c.id for c in cad.buscar_nome("maria")], [1])
        cad.remover(1)
        with self.assertRaises(KeyError):
            cad.obter(1)
        cad.cadastrar("Maria Silva", CPF)  # liberado após remoção


if __name__ == "__main__":
    unittest.main()
