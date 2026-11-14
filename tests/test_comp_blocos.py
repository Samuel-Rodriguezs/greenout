import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_blocos import (alcancaveis, arestas_de_retorno, construir_cfg,
                         dominadores, linearizar, ordem_pos_ordem_reversa,
                         para_dot, remover_inalcancaveis)
from comp_parser import parse
from comp_tac import Retorna, executar_tac, gerar_tac


def cfg_de(fonte, funcao=None):
    p = gerar_tac(parse(fonte))
    f = p.principal if funcao is None else next(f for f in p.funcoes if f.nome == funcao)
    return construir_cfg(f.codigo)


class TestBlocos(unittest.TestCase):
    def test_linha_reta_um_bloco(self):
        cfg = cfg_de("var a = 1; var b = a + 2; print(b);")
        self.assertEqual(len(cfg.blocos), 1)
        self.assertEqual(cfg.entrada.sucessores, [])

    def test_if_else_losango(self):
        cfg = cfg_de("var x = 2; if (x < 3) { print(x); } else { print(0); }")
        self.assertEqual(len(cfg.blocos), 4)
        self.assertEqual([b.sucessores for b in cfg.blocos], [[1, 2], [3], [3], []])
        self.assertEqual(sorted(cfg.bloco(3).predecessores), [1, 2])
        self.assertEqual(cfg.bloco(2).rotulo, "L2")

    def test_if_sem_else(self):
        cfg = cfg_de("var x = 2; if (x < 3) { print(x); } print(9);")
        self.assertEqual([b.sucessores for b in cfg.blocos], [[1, 2], [2], []])

    def test_while_tem_aresta_de_retorno(self):
        cfg = cfg_de("var i = 0; while (i < 3) { i = i + 1; } print(i);")
        # B0: init | B1: topo (teste) | B2: corpo + goto | B3: fim
        self.assertEqual([b.sucessores for b in cfg.blocos], [[1], [2, 3], [1], []])
        self.assertEqual(arestas_de_retorno(cfg), [(2, 1)])

    def test_dominadores(self):
        cfg = cfg_de("var x = 2; if (x < 3) { print(x); } else { print(0); }")
        dom = dominadores(cfg)
        self.assertEqual(dom[0], {0})
        self.assertEqual(dom[1], {0, 1})
        self.assertEqual(dom[3], {0, 3})  # nenhum ramo domina a junção

    def test_ordem_reversa_pos_ordem(self):
        cfg = cfg_de("var x = 2; if (x < 3) { print(x); } else { print(0); }")
        ordem = ordem_pos_ordem_reversa(cfg)
        self.assertEqual(ordem[0], 0)
        self.assertEqual(ordem[-1], 3)
        self.assertEqual(set(ordem), {0, 1, 2, 3})

    def test_codigo_inalcancavel(self):
        fonte = "func f() -> int { return 1; print(2); return 3; } print(f());"
        cfg = cfg_de(fonte, "f")
        self.assertEqual(alcancaveis(cfg), {0})
        limpo = remover_inalcancaveis(cfg)
        self.assertEqual(len(limpo.blocos), 1)
        self.assertEqual(limpo.entrada.instrs[-1], Retorna(1))

    def test_remocao_preserva_comportamento(self):
        fonte = """
        func f(n: int) -> int {
            while (n > 0) { if (n == 3) { return 100; return 200; } n = n - 1; }
            return n;
        }
        print(f(5)); print(f(2));
        """
        p = gerar_tac(parse(fonte))
        fn = p.funcoes[0]
        fn.codigo = linearizar(remover_inalcancaveis(construir_cfg(fn.codigo)))
        self.assertEqual(executar_tac(p), ["100", "0"])

    def test_predecessores_consistentes(self):
        cfg = cfg_de("var i = 0; while (i < 5) { if (i == 2) { print(i); } i = i + 1; }")
        for b in cfg.blocos:
            for s in b.sucessores:
                self.assertIn(b.id, cfg.bloco(s).predecessores)

    def test_linearizar_devolve_codigo_original(self):
        p = gerar_tac(parse("var i = 0; while (i < 5) { i = i + 1; } print(i);"))
        self.assertEqual(linearizar(construir_cfg(p.principal.codigo)), p.principal.codigo)

    def test_codigo_vazio(self):
        cfg = construir_cfg([])
        self.assertEqual(len(cfg.blocos), 1)
        self.assertEqual(alcancaveis(cfg), {0})

    def test_dot(self):
        dot = para_dot(cfg_de("var x = 1; while (x < 3) { x = x + 1; }"), "g")
        self.assertTrue(dot.startswith("digraph g {"))
        self.assertIn("B1 -> B2;", dot)
        self.assertIn("B2 -> B1;", dot)
        self.assertTrue(dot.endswith("}"))


if __name__ == "__main__":
    unittest.main()
