import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fp_lentes import (
    IDENTIDADE, Lente, compor_todas, lente_campo, lente_chave, lente_indice,
    prisma_inteiro_de_texto, prisma_tipo,
)


@dataclass(frozen=True)
class Endereco:
    rua: str
    cep: str


@dataclass(frozen=True)
class Pessoa:
    nome: str
    endereco: Endereco


@dataclass(frozen=True)
class Circulo:
    raio: int


@dataclass(frozen=True)
class Quadrado:
    lado: int


class TestLentes(unittest.TestCase):
    def setUp(self):
        self.p = Pessoa("Ana", Endereco("Rua A", "123"))

    def verifica_leis(self, lente, s, v1, v2):
        self.assertEqual(lente.ver(lente.definir(s, v1)), v1)  # set-get
        self.assertEqual(lente.definir(s, lente.ver(s)), s)  # get-set
        self.assertEqual(
            lente.definir(lente.definir(s, v1), v2), lente.definir(s, v2)
        )  # set-set

    def test_leis_campo_chave_indice(self):
        self.verifica_leis(lente_campo("nome"), self.p, "B", "C")
        self.verifica_leis(lente_chave("k"), {"k": 1, "z": 2}, 5, 6)
        self.verifica_leis(lente_indice(1), (1, 2, 3), 9, 8)
        self.verifica_leis(lente_indice(0), [1, 2], 9, 8)

    def test_imutabilidade(self):
        nova = lente_campo("nome").definir(self.p, "Bia")
        self.assertEqual(self.p.nome, "Ana")
        self.assertEqual(nova.nome, "Bia")
        d = {"a": 1}
        lente_chave("a").definir(d, 2)
        self.assertEqual(d, {"a": 1})

    def test_over(self):
        self.assertEqual(lente_campo("nome").over(str.upper, self.p).nome, "ANA")
        self.assertEqual(lente_indice(1).over(lambda x: x * 10, (1, 2)), (1, 20))

    def test_composicao(self):
        cep = lente_campo("endereco") @ lente_campo("cep")
        self.assertEqual(cep.ver(self.p), "123")
        novo = cep.definir(self.p, "999")
        self.assertEqual(novo.endereco.cep, "999")
        self.assertEqual(novo.endereco.rua, "Rua A")
        self.assertEqual(self.p.endereco.cep, "123")
        self.verifica_leis(cep, self.p, "1", "2")

    def test_composicao_associativa_e_identidade(self):
        s = {"a": ({"b": [1, 2]}, 0)}
        a, b, c, d = lente_chave("a"), lente_indice(0), lente_chave("b"), lente_indice(1)
        esq = (a @ b) @ (c @ d)
        dir_ = a @ (b @ (c @ d))
        self.assertEqual(esq.ver(s), 2)
        self.assertEqual(esq.definir(s, 7), dir_.definir(s, 7))
        self.assertEqual(compor_todas(a, b, c, d).definir(s, 7), {"a": ({"b": [1, 7]}, 0)})
        l = lente_campo("nome")
        self.assertEqual((IDENTIDADE @ l).ver(self.p), l.ver(self.p))
        self.assertEqual((l @ IDENTIDADE).definir(self.p, "Z"), l.definir(self.p, "Z"))

    def test_lente_customizada(self):
        celsius = Lente(lambda f: (f - 32) * 5 / 9, lambda f, c: c * 9 / 5 + 32)
        self.assertEqual(celsius.over(lambda c: c + 10, 32), 50.0)

    def test_prisma_tipo(self):
        p = prisma_tipo(Circulo)
        self.assertEqual(p.preview(Circulo(2)), Circulo(2))
        self.assertIsNone(p.preview(Quadrado(2)))
        self.assertEqual(p.over(lambda c: Circulo(c.raio + 1), Circulo(2)), Circulo(3))
        q = Quadrado(5)
        self.assertIs(p.over(lambda c: c, q), q)
        self.assertIs(p.definir(q, Circulo(1)), q)

    def test_prisma_inteiro(self):
        p = prisma_inteiro_de_texto()
        self.assertEqual(p.preview("42"), 42)
        self.assertIsNone(p.preview("042"))
        self.assertIsNone(p.preview("abc"))
        self.assertIsNone(p.preview(7))
        self.assertEqual(p.review(5), "5")
        self.assertEqual(p.preview(p.review(-12)), -12)  # review-preview
        self.assertEqual(p.over(lambda n: n + 1, "9"), "10")
        self.assertEqual(p.over(lambda n: n + 1, "x"), "x")

    def test_prisma_composto_e_com_lente(self):
        p = prisma_tipo(Circulo).compor(prisma_tipo(Circulo))
        self.assertEqual(p.preview(Circulo(1)), Circulo(1))
        raio = prisma_tipo(Circulo).compor_lente(lente_campo("raio"))
        self.assertEqual(raio.preview(Circulo(3)), 3)
        self.assertEqual(raio.over(lambda r: r * 2, Circulo(3)), Circulo(6))
        self.assertEqual(raio.over(lambda r: r * 2, Quadrado(3)), Quadrado(3))


if __name__ == "__main__":
    unittest.main()
