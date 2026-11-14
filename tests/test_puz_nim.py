import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_nim import (grundy, grundy_kayles, grundy_subtracao, jogada_misere,
                     jogada_vencedora, mex, nim_sum, vence_soma_de_jogos)


def jogador_perde_normal(pilhas, memo={}):
    chave = tuple(sorted(pilhas))
    if chave not in memo:
        memo[chave] = all(
            not jogador_perde_normal(chave[:i] + (p - k,) + chave[i + 1:])
            for i, p in enumerate(chave) for k in range(1, p + 1)
        ) if any(chave) else True
    return memo[chave]


def jogador_vence_misere(pilhas, memo={}):
    chave = tuple(sorted(pilhas))
    if chave not in memo:
        if not any(chave):
            memo[chave] = True  # o adversário tirou o último e perdeu
        else:
            memo[chave] = any(
                not jogador_vence_misere(chave[:i] + (p - k,) + chave[i + 1:])
                for i, p in enumerate(chave) for k in range(1, p + 1)
            )
    return memo[chave]


class TestNim(unittest.TestCase):
    def test_nim_sum(self):
        self.assertEqual(nim_sum([3, 4, 5]), 2)
        self.assertEqual(nim_sum([]), 0)

    def test_jogada_vencedora(self):
        i, q = jogada_vencedora([3, 4, 5])
        pilhas = [3, 4, 5]
        pilhas[i] -= q
        self.assertEqual(nim_sum(pilhas), 0)

    def test_posicao_perdedora(self):
        self.assertIsNone(jogada_vencedora([1, 2, 3]))
        self.assertIsNone(jogada_vencedora([0, 0]))

    def test_concorda_com_forca_bruta(self):
        for a in range(5):
            for b in range(5):
                for c in range(4):
                    self.assertEqual(jogada_vencedora([a, b, c]) is None,
                                     jogador_perde_normal([a, b, c]))

    def test_misere_concorda_com_forca_bruta(self):
        for a in range(5):
            for b in range(5):
                for c in range(4):
                    p = [a, b, c]
                    if not any(p):
                        continue
                    jogada = jogada_misere(p)
                    self.assertEqual(jogada is not None, jogador_vence_misere(p), p)
                    if jogada:
                        i, q = jogada
                        self.assertTrue(1 <= q <= p[i], p)
                        p[i] -= q
                        # após a jogada, o adversário deve estar em posição perdedora
                        self.assertFalse(jogador_vence_misere(p) if any(p) else False, (a, b, c))

    def test_mex(self):
        self.assertEqual(mex(set()), 0)
        self.assertEqual(mex({0, 1, 3}), 2)

    def test_grundy_de_pilha_de_nim_e_o_tamanho(self):
        mov = lambda n: [n - k for k in range(1, n + 1)]
        for n in range(8):
            self.assertEqual(grundy(n, mov), n)

    def test_subtracao_1_2_3_e_mod_4(self):
        for n in range(20):
            self.assertEqual(grundy_subtracao(n, (1, 2, 3)), n % 4)

    def test_subtracao_2_5(self):
        self.assertEqual([grundy_subtracao(n, (2, 5)) for n in range(10)],
                         [0, 0, 1, 1, 0, 2, 1, 0, 0, 1])

    def test_soma_de_jogos(self):
        g = [grundy_subtracao(n, (1, 2, 3)) for n in (5, 6, 7)]  # 1, 2, 3
        self.assertFalse(vence_soma_de_jogos(g))
        self.assertTrue(vence_soma_de_jogos([1, 2, 4]))

    def test_kayles(self):
        # sequência conhecida de Grundy do Kayles
        self.assertEqual([grundy_kayles(n) for n in range(12)], [0, 1, 2, 3, 1, 4, 3, 2, 1, 4, 2, 6])


if __name__ == "__main__":
    unittest.main()
