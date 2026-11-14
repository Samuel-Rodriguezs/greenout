import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from tipos_algebricos import (Con, ErroTipo, PCon, PCoringa, PLit, PVar,
                              Universo, casar, eliminar, escolher,
                              tipar_padrao, universo_padrao, verificar_valor)
from tipos_unificacao import BOOL, INT, TCon, TVar, lista

U = universo_padrao()
NIL = Con("Nil")


def cons(x, xs):
    return Con("Cons", (x, xs))


def opcao(t):
    return TCon("Opcao", (t,))


class TestAlgebricos(unittest.TestCase):
    def test_valores_bem_tipados(self):
        self.assertTrue(verificar_valor(Con("Algum", (3,)), opcao(INT), U))
        self.assertTrue(verificar_valor(Con("Nada"), opcao(BOOL), U))
        self.assertTrue(verificar_valor(cons(1, cons(2, NIL)), lista(INT), U))

    def test_valores_mal_tipados(self):
        self.assertFalse(verificar_valor(Con("Algum", (True,)), opcao(INT), U))
        self.assertFalse(verificar_valor(cons(1, cons(True, NIL)), lista(INT), U))
        self.assertFalse(verificar_valor(Con("Algum", (1,)), lista(INT), U))
        self.assertFalse(verificar_valor(Con("Algum"), opcao(INT), U))  # aridade
        self.assertFalse(verificar_valor(True, INT, U))
        self.assertFalse(verificar_valor(1, BOOL, U))

    def test_produto(self):
        v = Con("MkPar", (1, True))
        self.assertTrue(verificar_valor(v, TCon("Par", (INT, BOOL)), U))
        self.assertFalse(verificar_valor(v, TCon("Par", (BOOL, INT)), U))

    def test_soma(self):
        t = TCon("Ou", (INT, BOOL))
        self.assertTrue(verificar_valor(Con("Esq", (1,)), t, U))
        self.assertTrue(verificar_valor(Con("Dir", (False,)), t, U))
        self.assertFalse(verificar_valor(Con("Esq", (False,)), t, U))

    def test_tipar_padrao(self):
        p = PCon("Cons", (PVar("x"), PVar("resto")))
        self.assertEqual(tipar_padrao(p, lista(INT), U), {"x": INT, "resto": lista(INT)})

    def test_tipar_padrao_aninhado(self):
        p = PCon("Algum", (PCon("MkPar", (PVar("a"), PCoringa())),))
        t = opcao(TCon("Par", (BOOL, INT)))
        self.assertEqual(tipar_padrao(p, t, U), {"a": BOOL})

    def test_tipar_padrao_erros(self):
        with self.assertRaises(ErroTipo):
            tipar_padrao(PCon("Cons", (PVar("x"),)), lista(INT), U)  # aridade
        with self.assertRaises(ErroTipo):
            tipar_padrao(PCon("Nil"), opcao(INT), U)  # tipo errado
        with self.assertRaises(ErroTipo):
            tipar_padrao(PLit(1), BOOL, U)
        with self.assertRaises(ErroTipo):
            tipar_padrao(PCon("Cons", (PVar("x"), PVar("x"))), lista(INT), U)
        with self.assertRaises(ErroTipo):
            tipar_padrao(PCon("Fantasma"), lista(INT), U)

    def test_casar(self):
        self.assertEqual(casar(PVar("x"), 5), {"x": 5})
        self.assertEqual(casar(PCoringa(), 5), {})
        self.assertIsNone(casar(PLit(1), 2))
        self.assertIsNone(casar(PLit(1), True))
        self.assertIsNone(casar(PLit(True), 1))
        self.assertEqual(casar(PLit(True), True), {})
        v = cons(1, cons(2, NIL))
        p = PCon("Cons", (PVar("h"), PCon("Cons", (PVar("s"), PCoringa()))))
        self.assertEqual(casar(p, v), {"h": 1, "s": 2})
        self.assertIsNone(casar(p, cons(1, NIL)))

    def test_escolher_soma_lista(self):
        def soma(v):
            return escolher(v, [
                (PCon("Nil"), lambda b: 0),
                (PCon("Cons", (PVar("h"), PVar("t"))), lambda b: b["h"] + soma(b["t"])),
            ])
        self.assertEqual(soma(cons(1, cons(2, cons(3, NIL)))), 6)
        self.assertEqual(soma(NIL), 0)

    def test_escolher_primeiro_ramo_vence(self):
        r = escolher(5, [(PLit(5), lambda b: "cinco"), (PVar("n"), lambda b: "outro")])
        self.assertEqual(r, "cinco")
        r = escolher(6, [(PLit(5), lambda b: "cinco"), (PVar("n"), lambda b: "outro")])
        self.assertEqual(r, "outro")

    def test_escolher_sem_casamento(self):
        with self.assertRaises(LookupError):
            escolher(NIL, [(PCon("Cons", (PCoringa(), PCoringa())), lambda b: 1)])

    def test_eliminar(self):
        casos = {"Nada": lambda: "vazio", "Algum": lambda x: x * 2}
        self.assertEqual(eliminar(Con("Algum", (21,)), casos, U), 42)
        self.assertEqual(eliminar(Con("Nada"), casos, U), "vazio")

    def test_eliminar_exige_todos_os_casos(self):
        with self.assertRaises(ErroTipo):
            eliminar(Con("Nada"), {"Nada": lambda: 0}, U)
        with self.assertRaises(ErroTipo):
            eliminar(Con("Nada"), {"Nada": lambda: 0, "Algum": lambda x: x, "X": lambda: 1}, U)

    def test_declaracao_invalida(self):
        u = Universo()
        u.declarar("T", ("a",), {"A": (TVar("a"),)})
        with self.assertRaises(ErroTipo):
            u.declarar("T", (), {"B": ()})
        with self.assertRaises(ErroTipo):
            u.declarar("S", (), {"A": ()})  # construtor repetido
        with self.assertRaises(ErroTipo):
            u.declarar("V", (), {})  # vazio
        with self.assertRaises(ErroTipo):
            u.declarar("W", (), {"W1": (TVar("z"),)})  # variável livre

    def test_par_de_lista(self):
        v = Con("MkPar", (cons(1, NIL), Con("Nada")))
        self.assertTrue(verificar_valor(v, TCon("Par", (lista(INT), opcao(BOOL))), U))


if __name__ == "__main__":
    unittest.main()
