import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_blocos import construir_cfg
from comp_gerador import gerar
from comp_parser import parse
from comp_regalloc import (alocar, colorir, coloracao_valida,
                           grafo_de_interferencia, renomear)
from comp_tac import ProgramaTAC, executar_tac, gerar_tac
from comp_vm import executar


def grafo_de(arestas, extras=()):
    g = {n: set() for n in extras}
    for a, b in arestas:
        g.setdefault(a, set()).add(b)
        g.setdefault(b, set()).add(a)
    return g


FONTE = """
func fib(n: int) -> int {
    var a = 0; var b = 1; var i = 0;
    while (i < n) { var t = a + b; a = b; b = t; i = i + 1; }
    return a;
}
func primo(n: int) -> bool {
    if (n < 2) { return false; }
    var d = 2;
    while (d * d <= n) { if (n % d == 0) { return false; } d = d + 1; }
    return true;
}
var k = 0;
while (k < 12) { print(fib(k)); if (primo(k)) { print(k * 100); } k = k + 1; }
print(1 < 2 && primo(7) || primo(8));
"""


class TestColoracao(unittest.TestCase):
    def test_grafo_vazio(self):
        a = colorir({}, 3)
        self.assertEqual(a.cores, {})

    def test_cadeia_usa_duas_cores(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("c", "d")])
        a = colorir(g, 2)
        self.assertEqual(a.derramados, set())
        self.assertTrue(coloracao_valida(g, a))

    def test_triangulo_com_tres_cores(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("a", "c")])
        a = colorir(g, 3)
        self.assertEqual(a.registradores_usados, 3)
        self.assertTrue(coloracao_valida(g, a))

    def test_triangulo_com_duas_cores_derrama_um(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("a", "c")])
        a = colorir(g, 2)
        self.assertEqual(len(a.derramados), 1)
        self.assertEqual(len(a.cores), 2)
        self.assertTrue(coloracao_valida(g, a))

    def test_otimismo_colore_ciclo_de_quatro_com_duas_cores(self):
        # todos os nós têm grau 2 (não < 2), mas o ciclo é 2-colorível
        g = grafo_de([("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")])
        a = colorir(g, 2)
        self.assertEqual(a.derramados, set())
        self.assertTrue(coloracao_valida(g, a))

    def test_k4_com_tres_cores(self):
        nomes = "abcd"
        g = grafo_de([(x, y) for i, x in enumerate(nomes) for y in nomes[i + 1:]])
        a = colorir(g, 3)
        self.assertEqual(len(a.derramados), 1)

    def test_isolados_compartilham_cor(self):
        a = colorir(grafo_de([], "xyz"), 1)
        self.assertEqual(set(a.cores.values()), {0})

    def test_deterministico(self):
        g = grafo_de([("a", "b"), ("b", "c"), ("a", "c"), ("c", "d")])
        self.assertEqual(colorir(g, 2), colorir(g, 2))


class TestInterferencia(unittest.TestCase):
    def test_vivas_simultaneas_interferem(self):
        p = gerar_tac(parse("var a = 1; var b = 2; print(a + b);"))
        g = grafo_de_interferencia(construir_cfg(p.principal.codigo))
        self.assertIn("b", g["a"])

    def test_variaveis_de_vidas_disjuntas_nao_interferem(self):
        p = gerar_tac(parse("var a = 1; print(a); var b = 2; print(b);"))
        g = grafo_de_interferencia(construir_cfg(p.principal.codigo))
        self.assertNotIn("b", g["a"])

    def test_copia_nao_interfere_com_a_origem(self):
        p = gerar_tac(parse("var a = 1; var b = a; print(a + b);"))
        g = grafo_de_interferencia(construir_cfg(p.principal.codigo))
        self.assertNotIn("b", g["a"])

    def test_parametros_interferem_entre_si(self):
        p = gerar_tac(parse("func f(a: int, b: int) -> int { return 1; } print(f(1, 2));"))
        f = p.funcoes[0]
        aloc, g = alocar(f.codigo, 4, f.params)
        self.assertNotEqual(aloc.cores["a"], aloc.cores["b"])

    def test_simetria(self):
        p = gerar_tac(parse(FONTE))
        for f in p.funcoes + [p.principal]:
            g = grafo_de_interferencia(construir_cfg(f.codigo))
            for a, vs in g.items():
                for b in vs:
                    self.assertIn(a, g[b])


class TestAlocacaoEndToEnd(unittest.TestCase):
    def reescrever(self, k):
        p = gerar_tac(parse(FONTE))
        novas = []
        derramou = False
        for f in p.funcoes + [p.principal]:
            aloc, g = alocar(f.codigo, k, f.params)
            self.assertTrue(coloracao_valida(g, aloc))
            derramou = derramou or bool(aloc.derramados)
            novas.append(renomear(f, aloc))
        return ProgramaTAC(novas[:-1], novas[-1]), derramou

    def test_programa_equivalente_com_varios_k(self):
        esperado = executar(gerar(parse(FONTE))).saida
        for k in (2, 3, 4, 8):
            novo, _ = self.reescrever(k)
            self.assertEqual(executar_tac(novo), esperado, f"k={k}")

    def test_k_pequeno_derrama_e_k_grande_nao(self):
        _, derramou_2 = self.reescrever(2)
        _, derramou_16 = self.reescrever(16)
        self.assertTrue(derramou_2)
        self.assertFalse(derramou_16)

    def test_nomes_resultantes_sao_registradores_ou_memoria(self):
        novo, _ = self.reescrever(3)
        nomes = set()
        for f in novo.funcoes + [novo.principal]:
            nomes.update(f.params)
        self.assertTrue(all(n[0] in "rm" and n[1:].isdigit() for n in nomes))

    def test_menos_registradores_que_variaveis(self):
        p = gerar_tac(parse(FONTE))
        fib = p.funcoes[0]
        aloc, g = alocar(fib.codigo, 8, fib.params)
        self.assertLess(aloc.registradores_usados, len(g))


if __name__ == "__main__":
    unittest.main()
