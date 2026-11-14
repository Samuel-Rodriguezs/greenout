import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_cifra_substituicao import (ALFABETO, FREQ_PT, chave_aleatoria,
                                    chave_por_frequencia, cifrar,
                                    contar_letras, decifrar, modelo_bigramas,
                                    quebrar)

CORPUS = """
A programacao e a arte de organizar ideias em passos que uma maquina consegue executar.
Cada problema pequeno resolvido com cuidado ajuda a entender os problemas maiores que
aparecem depois. Quem estuda algoritmos aprende que existem muitas formas de chegar ao
mesmo resultado, e que a escolha entre elas depende do tempo disponivel e da memoria que
se pode gastar. Os testes servem para garantir que o programa continua fazendo o que deve
fazer mesmo depois de muitas mudancas. Uma boa pratica e escrever primeiro o teste e so
depois o codigo, assim o resultado esperado fica claro desde o inicio do trabalho.
Os jogos de logica sao um excelente treino para a mente, pois exigem paciencia, atencao e
a capacidade de testar hipoteses sem medo de errar. Quando uma tentativa falha, o jogador
volta atras e escolhe outro caminho, exatamente como faz um programa de busca com retrocesso.
"""

SEGREDO = """
Os problemas de busca sao resolvidos quando se escolhe uma boa representacao para o estado.
Depois disso, o programa explora as possibilidades uma a uma, descartando os caminhos que nao
levam a lugar nenhum, e guarda o que ja foi visto para nao repetir o mesmo trabalho.
"""


class TestCifraSubstituicao(unittest.TestCase):
    def test_roundtrip_mantem_caixa_e_pontuacao(self):
        chave = chave_aleatoria(3)
        texto = "Olá, Mundo! 42 testes."
        cifrado = cifrar(texto, chave)
        self.assertNotEqual(cifrado, texto)
        self.assertEqual(decifrar(cifrado, chave), texto)
        self.assertEqual(cifrado[-8:].count(" "), texto[-8:].count(" "))

    def test_chave_conhecida(self):
        chave = "zyxwvutsrqponmlkjihgfedcba"  # atbash
        self.assertEqual(cifrar("abc", chave), "zyx")

    def test_chave_invalida(self):
        with self.assertRaises(ValueError):
            cifrar("abc", "abc")
        with self.assertRaises(ValueError):
            decifrar("abc", "a" * 26)

    def test_contagem(self):
        self.assertEqual(contar_letras("Aa b!")["a"], 2)

    def test_chave_por_frequencia_e_permutacao(self):
        chave = chave_por_frequencia(cifrar(CORPUS, chave_aleatoria(1)))
        self.assertEqual(sorted(chave), list(ALFABETO))

    def test_frequencias_somam_proximo_de_cem(self):
        self.assertAlmostEqual(sum(FREQ_PT.values()), 100, delta=3)

    def test_quebra_recupera_maior_parte_do_texto(self):
        modelo = modelo_bigramas(CORPUS)
        chave = chave_aleatoria(42)
        cifrado = cifrar(SEGREDO, chave)
        _, claro = quebrar(cifrado, modelo, seed=1)
        iguais = sum(a == b for a, b in zip(claro, SEGREDO))
        self.assertGreater(iguais / len(SEGREDO), 0.75)


if __name__ == "__main__":
    unittest.main()
