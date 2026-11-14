import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from web_injecao import Container, ErroInjecao


class Config:
    def __init__(self, url: str = "sqlite://"):
        self.url = url


class Banco:
    def __init__(self, config: Config):
        self.config = config


class Repo:
    def __init__(self, banco: Banco, prefixo: str = "pre"):
        self.banco = banco
        self.prefixo = prefixo


class A:
    def __init__(self, b: "B"):
        self.b = b


class B:
    def __init__(self, a: A):
        self.a = a


class TestWebInjecao(unittest.TestCase):
    def test_autowiring_por_tipo(self):
        c = Container()
        repo = c.resolver(Repo)
        self.assertIsInstance(repo.banco.config, Config)
        self.assertEqual(repo.prefixo, "pre")

    def test_singleton_compartilhado(self):
        c = Container()
        c.registrar(Config)
        self.assertIs(c.resolver(Config), c.resolver(Config))
        c.registrar(Banco)
        self.assertIs(c.resolver(Banco).config, c.resolver(Config))

    def test_transiente(self):
        c = Container()
        c.registrar(Config, escopo="transiente")
        self.assertIsNot(c.resolver(Config), c.resolver(Config))

    def test_instancia_pronta_e_por_nome(self):
        c = Container()
        c.registrar(Config, instancia=Config("pg://x"))
        c.registrar("prefixo", lambda: "custom")
        r = c.resolver(Repo)
        self.assertEqual(r.banco.config.url, "pg://x")
        self.assertEqual(r.prefixo, "custom")

    def test_chamar_funcao_com_explicitos(self):
        c = Container()

        def handler(banco: Banco, id: int):
            return banco, id

        banco, id_ = c.chamar(handler, id=7)
        self.assertIsInstance(banco, Banco)
        self.assertEqual(id_, 7)

    def test_escopo_de_requisicao(self):
        c = Container()
        c.registrar(Config)
        c.registrar(Banco, escopo="requisicao")
        r1, r2 = c.novo_escopo(), c.novo_escopo()
        self.assertIs(r1.resolver(Banco), r1.resolver(Banco))
        self.assertIsNot(r1.resolver(Banco), r2.resolver(Banco))
        self.assertIs(r1.resolver(Config), r2.resolver(Config))

    def test_ciclo(self):
        with self.assertRaises(ErroInjecao) as cm:
            Container().resolver(A)
        self.assertIn("circular", str(cm.exception))

    def test_nao_resolvivel(self):
        def f(x):
            return x
        with self.assertRaises(ErroInjecao):
            Container().chamar(f)
        with self.assertRaises(ErroInjecao):
            Container().resolver("nome-inexistente")

    def test_escopo_invalido_e_registro_invalido(self):
        c = Container()
        with self.assertRaises(ValueError):
            c.registrar(Config, escopo="eterno")
        with self.assertRaises(ValueError):
            c.registrar("x")

    def test_ciclo_nao_deixa_estado_sujo(self):
        c = Container()
        with self.assertRaises(ErroInjecao):
            c.resolver(A)
        with self.assertRaises(ErroInjecao) as cm:
            c.resolver(A)
        self.assertIn("circular", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
