import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from puz_palavras_cruzadas import extrair_slots, preencher, validar

DIC = (
    "casa sapo rato gato ovo uva oca bolo cada asas "
    "sala polo tapa mesa rua sol lua ola ato ela "
    "eco era ira ave eva uso ora ovos pato ouro "
    "osso aula alma lama rima luar mala mapa pera rede "
    "reta roda sede seta sela taco tela uvas vaso veia "
    "vela vida lado lago laco lata leao lote lobo moda "
    "modo mola mora mosa nave nota "
).split()


class TestPalavrasCruzadas(unittest.TestCase):
    def test_extrair_slots(self):
        slots = extrair_slots(["..#", "...", "#.."])
        horizontais = [s for s in slots if s[0][0] == s[-1][0]]
        verticais = [s for s in slots if s[0][1] == s[-1][1]]
        self.assertEqual(len(horizontais), 3)
        self.assertEqual(len(verticais), 3)

    def test_celula_isolada_nao_e_slot(self):
        self.assertEqual(extrair_slots([".#.", "###", ".#."]), [])

    def test_quadrado_4x4_com_repeticao(self):
        grade = preencher(["....", "....", "....", "...."], DIC, unicas=False)
        self.assertEqual(grade, ["casa", "asas", "sala", "asas"])
        self.assertTrue(validar(grade, DIC))

    def test_quadrado_exige_repeticao(self):
        # um quadrado simétrico repete palavras: com `unicas` não existe solução neste dicionário
        self.assertIsNone(preencher(["...", "...", "..."], DIC))
        grade = preencher(["...", "...", "..."], DIC, unicas=False)
        self.assertIsNotNone(grade)
        self.assertTrue(validar(grade, DIC))

    def test_moldura_com_bloqueio_central(self):
        grade = preencher(["...", ".#.", "..."], DIC)
        self.assertEqual(grade, ["uva", "s#t", "ovo"])
        self.assertTrue(validar(grade, DIC))

    def test_respeita_pistas(self):
        grade = preencher(["u..", ".#.", "..."], DIC)
        self.assertEqual(grade[0][0], "u")
        self.assertTrue(validar(grade, DIC))
        self.assertIsNone(preencher(["z..", ".#.", "..."], DIC))

    def test_sem_solucao(self):
        self.assertIsNone(preencher(["..", ".."], ["ab", "cd"]))  # colunas exigem outras palavras
        self.assertIsNone(preencher(["....."], DIC))             # nenhuma palavra de 5 letras

    def test_molde_irregular(self):
        with self.assertRaises(ValueError):
            extrair_slots(["..", "."])

    def test_dois_por_dois_simetrico(self):
        grade = preencher(["..", ".."], ["ab", "ac", "bd", "cd", "ad"], unicas=False)
        self.assertIsNotNone(grade)
        self.assertTrue(validar(grade, ["ab", "ac", "bd", "cd", "ad"]))


if __name__ == "__main__":
    unittest.main()
