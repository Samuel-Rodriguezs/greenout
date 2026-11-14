import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_blocos import construir_cfg
from comp_parser import parse
from comp_tac import Bin, Copia, Imprime, Retorna, gerar_tac
from comp_vivacidade import analisar_vivacidade, definicoes_mortas, pontos_vivos


def analisa(fonte, funcao=None):
    p = gerar_tac(parse(fonte))
    f = p.principal if funcao is None else next(f for f in p.funcoes if f.nome == funcao)
    cfg = construir_cfg(f.codigo)
    return cfg, analisar_vivacidade(cfg)


class TestVivacidade(unittest.TestCase):
    def test_linha_reta(self):
        cfg, v = analisa("var a = 1; var b = 2; var c = a + b; print(c);")
        pontos = pontos_vivos(cfg, v)[0]
        self.assertEqual(pontos[0].antes, frozenset())
        self.assertEqual(pontos[0].depois, frozenset({"a"}))
        self.assertEqual(pontos[2].instrucao, Bin("%t1", "+", "a", "b"))
        self.assertEqual(pontos[2].antes, frozenset({"a", "b"}))
        self.assertEqual(pontos[2].depois, frozenset({"%t1"}))
        self.assertEqual(v.saida[0], set())

    def test_parametros_vivos_na_entrada(self):
        cfg, v = analisa("func f(a: int, b: int) -> int { return a + b; } print(f(1, 2));", "f")
        self.assertEqual(v.entrada[0], {"a", "b"})

    def test_variavel_nao_usada_nao_e_viva_na_entrada(self):
        cfg, v = analisa("func f(a: int, b: int) -> int { return a; } print(f(1, 2));", "f")
        self.assertEqual(v.entrada[0], {"a"})

    def test_if_une_vivas_dos_ramos(self):
        fonte = """
        func f(c: bool, a: int, b: int) -> int {
            var r = 0;
            if (c) { r = a; } else { r = b; }
            return r;
        }
        print(f(true, 1, 2));
        """
        cfg, v = analisa(fonte, "f")
        # após o teste de c, a e b ainda podem ser lidos (um em cada ramo)
        self.assertEqual(v.saida[0], {"a", "b"})
        self.assertEqual(v.entrada[0], {"c", "a", "b"})
        self.assertEqual(v.entrada[3], {"r"})

    def test_laco_propaga_vivacidade_pelo_back_edge(self):
        fonte = """
        func soma(n: int) -> int {
            var s = 0; var i = 0;
            while (i < n) { s = s + i; i = i + 1; }
            return s;
        }
        print(soma(3));
        """
        cfg, v = analisa(fonte, "soma")
        topo = next(b.id for b in cfg.blocos if b.rotulo == "L1")
        self.assertEqual(v.entrada[topo], {"s", "i", "n"})
        corpo = topo + 1
        self.assertEqual(v.saida[corpo], {"s", "i", "n"})

    def test_ponto_fixo_precisa_de_varias_iteracoes(self):
        fonte = """
        func f(n: int) -> int {
            var a = 1; var b = 2; var c = 3;
            while (n > 0) { c = b; b = a; a = n; n = n - 1; }
            return c;
        }
        print(f(2));
        """
        cfg, v = analisa(fonte, "f")
        topo = next(b.id for b in cfg.blocos if b.rotulo == "L1")
        # c é devolvido se o laço não rodar; b e a alimentam c nas iterações seguintes
        self.assertEqual(v.entrada[topo], {"n", "a", "b", "c"})
        corpo = topo + 1
        self.assertEqual(v.entrada[corpo], {"n", "a", "b"})  # c é sobrescrito antes de ser lido

    def test_definicoes_mortas(self):
        cfg, v = analisa("var a = 1; var b = 2; print(a);")
        self.assertEqual(definicoes_mortas(cfg, v), [Copia("b", 2)])

    def test_definicao_morta_nao_inclui_chamadas(self):
        cfg, v = analisa("func f() -> int { print(1); return 2; } f();")
        self.assertEqual(definicoes_mortas(cfg, v), [])

    def test_instrucao_final_sem_vivas(self):
        cfg, v = analisa("var a = 1; print(a);")
        ultimo = pontos_vivos(cfg, v)[0][-1]
        self.assertEqual(ultimo.instrucao, Retorna(None))
        self.assertEqual(ultimo.antes, frozenset())
        self.assertEqual(pontos_vivos(cfg, v)[0][1].instrucao, Imprime("a"))


if __name__ == "__main__":
    unittest.main()
