import itertools
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_automato import DFA, EPSILON, NFA, ErroAutomato


def palavras(alfabeto: str, max_len: int):
    for n in range(max_len + 1):
        for p in itertools.product(alfabeto, repeat=n):
            yield "".join(p)


def dfa_paridade_de_uns() -> DFA:
    # aceita palavras binárias com número par de '1'
    return DFA({"par", "impar"}, {"0", "1"},
               {("par", "0"): "par", ("par", "1"): "impar",
                ("impar", "0"): "impar", ("impar", "1"): "par"}, "par", {"par"})


def nfa_termina_em_ab() -> NFA:
    return NFA({"q0", "q1", "q2"}, {"a", "b"},
               {("q0", "a"): {"q0", "q1"}, ("q0", "b"): {"q0"}, ("q1", "b"): {"q2"}}, "q0", {"q2"})


class TestAutomato(unittest.TestCase):
    def test_dfa(self):
        d = dfa_paridade_de_uns()
        self.assertTrue(d.aceita(""))
        self.assertTrue(d.aceita("0110"))
        self.assertFalse(d.aceita("111"))

    def test_dfa_simbolo_invalido(self):
        with self.assertRaises(ErroAutomato):
            dfa_paridade_de_uns().aceita("012")

    def test_dfa_parcial_estado_morto(self):
        d = DFA({"a", "b"}, {"x", "y"}, {("a", "x"): "b"}, "a", {"b"})
        self.assertTrue(d.aceita("x"))
        self.assertFalse(d.aceita("y"))
        self.assertFalse(d.aceita("xx"))

    def test_nfa(self):
        n = nfa_termina_em_ab()
        self.assertTrue(n.aceita("bbab"))
        self.assertFalse(n.aceita("abb"))
        self.assertFalse(n.aceita(""))

    def test_nfa_epsilon(self):
        # (a|b)* seguido de c via epsilon
        n = NFA({"0", "1", "2"}, {"a", "c"},
                {("0", "a"): {"0"}, ("0", EPSILON): {"1"}, ("1", "c"): {"2"}}, "0", {"2"})
        self.assertTrue(n.aceita("aaac"))
        self.assertTrue(n.aceita("c"))
        self.assertFalse(n.aceita("aaa"))

    def test_nfa_para_dfa_equivalente(self):
        n = nfa_termina_em_ab()
        d = n.para_dfa()
        for p in palavras("ab", 8):
            self.assertEqual(n.aceita(p), d.aceita(p), p)

    def test_minimizacao(self):
        # DFA redundante: 4 estados para "termina em 1"
        d = DFA({"a", "b", "c", "d"}, {"0", "1"},
                {("a", "0"): "b", ("a", "1"): "c", ("b", "0"): "a", ("b", "1"): "d",
                 ("c", "0"): "b", ("c", "1"): "d", ("d", "0"): "a", ("d", "1"): "c"},
                "a", {"c", "d"})
        m = d.minimizar()
        self.assertEqual(len(m.estados), 2)
        for p in palavras("01", 8):
            self.assertEqual(d.aceita(p), m.aceita(p), p)

    def test_minimizar_dfa_do_nfa(self):
        n = nfa_termina_em_ab()
        d = n.para_dfa()
        m = d.minimizar()
        self.assertLessEqual(len(m.estados), len(d.estados))
        for p in palavras("ab", 8):
            self.assertEqual(n.aceita(p), m.aceita(p), p)

    def test_definicoes_invalidas(self):
        with self.assertRaises(ErroAutomato):
            DFA({"a"}, {"x"}, {}, "z", set())
        with self.assertRaises(ErroAutomato):
            DFA({"a"}, {"x"}, {("a", "y"): "a"}, "a", set())
        with self.assertRaises(ErroAutomato):
            NFA({"a"}, {"x"}, {("a", "x"): {"b"}}, "a", set())


if __name__ == "__main__":
    unittest.main()
