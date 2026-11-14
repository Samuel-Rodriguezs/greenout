import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from sim_poker import (avaliar, distribuir, embaralhar, melhor_mao, nome_categoria, novo_baralho,
                       parse_carta, parse_mao)


class TestPoker(unittest.TestCase):
    def test_baralho(self):
        b = novo_baralho()
        self.assertEqual(len(b), 52)
        self.assertEqual(len(set(b)), 52)

    def test_embaralhar_seed(self):
        b = novo_baralho()
        a = embaralhar(b, random.Random(1))
        c = embaralhar(b, random.Random(1))
        self.assertEqual(a, c)
        self.assertNotEqual(a, b)
        self.assertEqual(sorted(a), sorted(b))
        self.assertEqual(b, novo_baralho())

    def test_distribuir(self):
        mao, resto = distribuir(embaralhar(novo_baralho(), random.Random(2)), 5)
        self.assertEqual((len(mao), len(resto)), (5, 47))
        with self.assertRaises(ValueError):
            distribuir(mao, 6)

    def test_categorias(self):
        casos = {
            "As Ks Qs Js Ts": "straight flush",
            "9h 9d 9s 9c 2h": "quadra",
            "3h 3d 3s 8c 8h": "full house",
            "2h 7h 9h Jh Kh": "flush",
            "5h 6d 7s 8c 9h": "sequência",
            "4h 4d 4s Kc 9h": "trinca",
            "4h 4d 7s 7c 9h": "dois pares",
            "4h 4d 7s Jc 9h": "par",
            "2h 4d 7s Jc 9h": "carta alta",
        }
        for texto, esperado in casos.items():
            self.assertEqual(nome_categoria(parse_mao(texto)), esperado, texto)

    def test_roda_menor_que_sequencia_seis(self):
        roda = parse_mao("Ah 2d 3s 4c 5h")
        seis = parse_mao("2h 3d 4s 5c 6h")
        self.assertEqual(nome_categoria(roda), "sequência")
        self.assertLess(avaliar(roda), avaliar(seis))

    def test_desempates(self):
        self.assertGreater(avaliar(parse_mao("Kh Kd 2s 3c 4h")), avaliar(parse_mao("Qh Qd As 3c 4h")))
        self.assertGreater(avaliar(parse_mao("Kh Kd 5s 3c 4h")), avaliar(parse_mao("Kc Ks 4s 3d 2h")))
        self.assertGreater(avaliar(parse_mao("3h 3d 3s 2c 2h")), avaliar(parse_mao("2h 2d 2s Ac Ah")))
        self.assertEqual(avaliar(parse_mao("Ah Kd 5s 3c 2h"))[0], avaliar(parse_mao("As Kc 5d 3h 2d"))[0])
        self.assertEqual(avaliar(parse_mao("Ah Kd 5s 3c 2h")), avaliar(parse_mao("As Kc 5d 3h 2d")))

    def test_dois_pares_ordem(self):
        a = parse_mao("Kh Kd 2s 2c 9h")
        b = parse_mao("Qh Qd Js Jc Ah")
        self.assertGreater(avaliar(a), avaliar(b))

    def test_melhor_mao_de_sete(self):
        cartas = parse_mao("Ah Kh Qh Jh Th 2c 3d")
        self.assertEqual(nome_categoria(melhor_mao(cartas)), "straight flush")
        cartas = parse_mao("2h 2d 2s 9c 9h Ad 5c")
        self.assertEqual(nome_categoria(melhor_mao(cartas)), "full house")
        with self.assertRaises(ValueError):
            melhor_mao(cartas[:4])

    def test_validacoes(self):
        with self.assertRaises(ValueError):
            parse_carta("1h")
        with self.assertRaises(ValueError):
            avaliar(parse_mao("Ah Ah 2d 3c 4s"))
        with self.assertRaises(ValueError):
            avaliar(parse_mao("Ah 2d 3c 4s"))


if __name__ == "__main__":
    unittest.main()
