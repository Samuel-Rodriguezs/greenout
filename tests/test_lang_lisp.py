import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_lisp import ErroLisp, executar, ler, tokenizar


class TestLisp(unittest.TestCase):
    def test_aritmetica(self):
        self.assertEqual(executar("(+ 1 2 (* 3 4))"), 15)
        self.assertEqual(executar("(/ 10 4)"), 2.5)
        self.assertEqual(executar("(- 5)"), -5)

    def test_define_e_if(self):
        self.assertEqual(executar("(define x 5) (if (> x 3) 'grande 'pequeno)"), "grande")

    def test_fatorial_recursivo(self):
        prog = "(define (fat n) (if (<= n 1) 1 (* n (fat (- n 1))))) (fat 10)"
        self.assertEqual(executar(prog), 3628800)

    def test_recursao_de_cauda_profunda(self):
        prog = "(define (soma n acc) (if (= n 0) acc (soma (- n 1) (+ acc n)))) (soma 5000 0)"
        self.assertEqual(executar(prog), 12502500)

    def test_closure(self):
        prog = "(define (somador n) (lambda (x) (+ x n))) ((somador 3) 4)"
        self.assertEqual(executar(prog), 7)

    def test_listas(self):
        self.assertEqual(executar("(map (lambda (x) (* x x)) '(1 2 3))"), [1, 4, 9])
        self.assertEqual(executar("(car (cdr (list 1 2 3)))"), 2)
        self.assertEqual(executar("(filter (lambda (x) (> x 1)) '(1 2 3))"), [2, 3])

    def test_let_e_comentario(self):
        self.assertEqual(executar("(let ((a 2) (b 3)) (* a b)) ; fim"), 6)

    def test_tokenizar(self):
        self.assertEqual(tokenizar("(a 'b)"), ["(", "a", "'", "b", ")"])

    def test_erros(self):
        for prog in ["(+ 1", ")", "(foo)", "(/ 1 0)", "(1 2)", '"abc']:
            with self.assertRaises(ErroLisp, msg=prog):
                executar(prog)

    def test_aridade(self):
        with self.assertRaises(ErroLisp):
            executar("((lambda (x) x) 1 2)")

    def test_ler_multiplas(self):
        self.assertEqual(len(ler("1 2 (3)")), 3)


if __name__ == "__main__":
    unittest.main()
