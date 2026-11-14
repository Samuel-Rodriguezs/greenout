import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_kinds import (STAR, TC, TV, ErroKind, ap, declarar_dados, fn, k,
                         kind_de, kinds_padrao, mostrar, verificar_kind)

KC = kinds_padrao()
INT, LISTA, MAYBE = TC("Int"), TC("Lista"), TC("Maybe")


class TestKinds(unittest.TestCase):
    def test_kinds_simples(self):
        self.assertEqual(kind_de(INT, KC), STAR)
        self.assertEqual(kind_de(LISTA, KC), k(STAR, STAR))
        self.assertEqual(kind_de(ap(LISTA, INT), KC), STAR)
        self.assertEqual(kind_de(ap(TC("Either"), INT), KC), k(STAR, STAR))

    def test_funcao(self):
        self.assertEqual(kind_de(fn(INT, ap(LISTA, INT)), KC), STAR)

    def test_aplicacao_excessiva(self):
        with self.assertRaises(ErroKind):
            kind_de(ap(INT, INT), KC)

    def test_argumento_de_kind_errado(self):
        with self.assertRaises(ErroKind):
            kind_de(ap(LISTA, MAYBE), KC)       # Maybe sem argumento
        with self.assertRaises(ErroKind):
            kind_de(fn(LISTA, INT), KC)         # Lista não é um tipo completo

    def test_construtor_desconhecido(self):
        with self.assertRaises(ErroKind):
            kind_de(TC("Fantasma"), KC)

    def test_variaveis_com_kind_dado(self):
        vs = {"f": k(STAR, STAR), "a": STAR}
        self.assertEqual(kind_de(ap(TV("f"), TV("a")), KC, vs), STAR)
        with self.assertRaises(ErroKind):
            kind_de(ap(TV("a"), TV("a")), KC, vs)

    def test_variavel_livre_inferida(self):
        # Lista m: m deve ser *, e o resultado é *
        self.assertEqual(kind_de(ap(LISTA, TV("m")), KC), STAR)
        # m a  sozinho: m :: k1 -> k2 -> resultado ?, default estrela
        self.assertEqual(kind_de(ap(TV("m"), INT), KC), STAR)

    def test_verificar_kind(self):
        verificar_kind(ap(LISTA, INT), STAR, KC)
        verificar_kind(LISTA, k(STAR, STAR), KC)
        with self.assertRaises(ErroKind):
            verificar_kind(LISTA, STAR, KC)

    def test_dados_simples(self):
        kc = kinds_padrao()
        # data Caixa a = Caixa a
        self.assertEqual(declarar_dados(kc, "Caixa", ("a",), [TV("a")]), k(STAR, STAR))

    def test_dados_recursivo(self):
        kc = kinds_padrao()
        # data Arvore a = Folha | No (Arvore a) a (Arvore a)
        arv = ap(TC("Arvore"), TV("a"))
        self.assertEqual(declarar_dados(kc, "Arvore", ("a",), [arv, TV("a"), arv]),
                         k(STAR, STAR))
        self.assertEqual(kind_de(ap(TC("Arvore"), INT), kc), STAR)

    def test_dados_de_ordem_superior(self):
        kc = kinds_padrao()
        # data Fix f = Fix (f (Fix f))   =>  Fix :: (* -> *) -> *
        fix = TC("Fix")
        kd = declarar_dados(kc, "Fix", ("f",), [ap(TV("f"), ap(fix, TV("f")))])
        self.assertEqual(kd, k(k(STAR, STAR), STAR))
        self.assertEqual(kind_de(ap(fix, LISTA), kc), STAR)
        with self.assertRaises(ErroKind):
            kind_de(ap(fix, INT), kc)

    def test_dados_com_parametro_de_kind_funtor(self):
        kc = kinds_padrao()
        # data Compose f g a = Compose (f (g a))  =>  (*->*) -> (*->*) -> * -> *
        kd = declarar_dados(kc, "Compose", ("f", "g", "a"),
                            [ap(TV("f"), ap(TV("g"), TV("a")))])
        self.assertEqual(kd, k(k(STAR, STAR), k(STAR, STAR), STAR, STAR))
        self.assertEqual(mostrar(kd), "(* -> *) -> (* -> *) -> * -> *")

    def test_parametro_nao_usado_vira_estrela(self):
        kc = kinds_padrao()
        self.assertEqual(declarar_dados(kc, "Fantasma", ("a",), [INT]), k(STAR, STAR))

    def test_dados_com_kind_inconsistente(self):
        kc = kinds_padrao()
        # data Ruim a = Ruim (a Int) (Lista a): a seria * -> * e *
        campos = [ap(TV("a"), INT), ap(LISTA, TV("a"))]
        with self.assertRaises(ErroKind):
            declarar_dados(kc, "Ruim", ("a",), campos)
        self.assertNotIn("Ruim", kc)

    def test_campo_deve_ser_tipo_completo(self):
        with self.assertRaises(ErroKind):
            declarar_dados(kinds_padrao(), "X", ("a",), [LISTA])

    def test_kind_infinito(self):
        # data Y a = Y (a a): a :: k -> k impossível
        with self.assertRaises(ErroKind):
            declarar_dados(kinds_padrao(), "Y", ("a",), [ap(TV("a"), TV("a"))])


if __name__ == "__main__":
    unittest.main()
