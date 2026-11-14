import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_relogios_logicos import (
    ANTES,
    CONCORRENTE,
    DEPOIS,
    IGUAL,
    Simulacao,
    comparar_vetores,
)


def cenario() -> Simulacao:
    s = Simulacao(3)
    s.local(0)  # e0
    s.envia(0, "m1")  # e1
    s.local(1)  # e2
    s.recebe(1, "m1")  # e3
    s.envia(1, "m2")  # e4
    s.local(2)  # e5
    s.recebe(2, "m2")  # e6
    return s


class TestRelogios(unittest.TestCase):
    def test_lamport_calculado_a_mao(self):
        s = cenario()
        self.assertEqual([e.lamport for e in s.eventos], [1, 2, 1, 3, 4, 1, 5])

    def test_vetores_calculados_a_mao(self):
        s = cenario()
        self.assertEqual(
            [e.vetor for e in s.eventos],
            [(1, 0, 0), (2, 0, 0), (0, 1, 0), (2, 2, 0), (2, 3, 0), (0, 0, 1), (2, 3, 2)],
        )

    def test_causalidade_exata_vetorial(self):
        s = cenario()
        e = s.eventos
        self.assertEqual(s.relacao(e[1], e[3]), ANTES)  # envio -> recebimento
        self.assertEqual(s.relacao(e[6], e[0]), DEPOIS)  # transitividade via m2
        self.assertEqual(s.relacao(e[2], e[1]), CONCORRENTE)
        self.assertEqual(s.relacao(e[5], e[0]), CONCORRENTE)
        self.assertEqual(s.relacao(e[3], e[3]), IGUAL)

    def test_lamport_nao_detecta_concorrencia(self):
        s = cenario()
        e2, e1 = s.eventos[2], s.eventos[1]
        self.assertLess(e2.lamport, e1.lamport)  # parece "antes"...
        self.assertEqual(s.relacao(e2, e1), CONCORRENTE)  # ...mas são concorrentes

    def test_a_antes_de_b_implica_lamport_menor(self):
        s = cenario()
        for a in s.eventos:
            for b in s.eventos:
                if s.relacao(a, b) == ANTES:
                    self.assertLess(a.lamport, b.lamport)

    def test_ordem_total_desempata_por_processo(self):
        s = cenario()
        self.assertEqual(
            [(e.lamport, e.proc) for e in s.ordem_total()],
            [(1, 0), (1, 1), (1, 2), (2, 0), (3, 1), (4, 1), (5, 2)],
        )

    def test_receber_com_relogio_local_maior(self):
        s = Simulacao(2)
        for _ in range(5):
            s.local(1)
        s.envia(0, "m")
        ev = s.recebe(1, "m")
        self.assertEqual(ev.lamport, 6)  # max(5, 1) + 1
        self.assertEqual(ev.vetor, (1, 6))

    def test_comparar_vetores_direto(self):
        self.assertEqual(comparar_vetores((1, 2), (1, 3)), ANTES)
        self.assertEqual(comparar_vetores((2, 2), (1, 2)), DEPOIS)
        with self.assertRaises(ValueError):
            comparar_vetores((1,), (1, 2))

    def test_erros(self):
        s = Simulacao(2)
        with self.assertRaises(ValueError):
            s.local(2)
        with self.assertRaises(ValueError):
            s.recebe(0, "fantasma")
        s.envia(0, "m")
        with self.assertRaises(ValueError):
            s.envia(1, "m")
        with self.assertRaises(ValueError):
            Simulacao(0)


if __name__ == "__main__":
    unittest.main()
