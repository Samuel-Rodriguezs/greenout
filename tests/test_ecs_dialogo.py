import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ecs_dialogo import Dialogo, GrafoDialogo, No, Opcao


def ferreiro():
    g = GrafoDialogo()
    g.adicionar(No("oi", "Ferreiro", "Bem-vindo!", [
        Opcao("Quero uma espada", "loja"),
        Opcao("Tenho o minério", "entrega", condicao=lambda v: v.get("minerio", 0) >= 3),
        Opcao("Tchau", None),
    ]))
    g.adicionar(No("loja", "Ferreiro", "Custa 50 moedas.", [
        Opcao("Comprar", "fim", condicao=lambda v: v["ouro"] >= 50,
              efeito=lambda v: v.update(ouro=v["ouro"] - 50, espada=True)),
        Opcao("Voltar", "oi"),
    ]))
    g.adicionar(No("entrega", "Ferreiro", "Ótimo!", [Opcao("...", "fim", efeito=lambda v: v.update(minerio=0))],
                   ao_entrar=lambda v: v.update(visitou_entrega=True)))
    g.adicionar(No("fim", "Ferreiro", "Volte sempre."))
    return g


class TestDialogo(unittest.TestCase):
    def test_opcoes_filtradas_por_condicao(self):
        d = Dialogo(ferreiro(), "oi", {"ouro": 100, "minerio": 1})
        self.assertEqual(d.opcoes(), [(0, "Quero uma espada"), (2, "Tchau")])
        d2 = Dialogo(ferreiro(), "oi", {"ouro": 100, "minerio": 3})
        self.assertEqual([i for i, _ in d2.opcoes()], [0, 1, 2])

    def test_fluxo_com_efeito_e_fim(self):
        d = Dialogo(ferreiro(), "oi", {"ouro": 80})
        d.escolher(0)
        self.assertEqual(d.atual.id, "loja")
        d.escolher(0)
        self.assertEqual(d.vars["ouro"], 30)
        self.assertTrue(d.vars["espada"])
        self.assertEqual(d.atual.id, "fim")
        d.continuar()
        self.assertTrue(d.terminou)
        self.assertEqual(d.historico, ["oi", "loja", "fim"])

    def test_opcao_indisponivel(self):
        d = Dialogo(ferreiro(), "oi", {"ouro": 10})
        d.escolher(0)
        self.assertEqual(d.opcoes(), [(1, "Voltar")])
        with self.assertRaises(ValueError):
            d.escolher(0)
        d.escolher(1)
        self.assertEqual(d.atual.id, "oi")

    def test_ao_entrar_e_continuar(self):
        d = Dialogo(ferreiro(), "oi", {"minerio": 3})
        d.escolher(1)
        self.assertTrue(d.vars["visitou_entrega"])
        d.continuar()  # única opção
        self.assertEqual((d.atual.id, d.vars["minerio"]), ("fim", 0))

    def test_continuar_com_varias_opcoes_falha(self):
        d = Dialogo(ferreiro(), "oi", {})
        with self.assertRaises(ValueError):
            d.continuar()

    def test_encerrado(self):
        d = Dialogo(ferreiro(), "oi", {})
        d.escolher(2)
        self.assertTrue(d.terminou)
        self.assertEqual(d.opcoes(), [])
        with self.assertRaises(RuntimeError):
            d.escolher(0)

    def test_validacao_do_grafo(self):
        g = GrafoDialogo()
        g.adicionar(No("a", "x", "t", [Opcao("ir", "z")]))
        g.adicionar(No("orfao", "x", "t"))
        erros = g.validar("a")
        self.assertIn("a: destino inexistente z", erros)
        self.assertIn("inalcançável: orfao", erros)
        self.assertEqual(g.validar("nada"), ["início inexistente: nada"])
        with self.assertRaises(ValueError):
            Dialogo(g, "a")
        with self.assertRaises(ValueError):
            g.adicionar(No("a", "x", "t"))

    def test_nao_altera_variaveis_do_chamador(self):
        v = {"ouro": 60}
        d = Dialogo(ferreiro(), "oi", v)
        d.escolher(0)
        d.escolher(0)
        self.assertEqual(v, {"ouro": 60})


if __name__ == "__main__":
    unittest.main()
