import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_logo import ErroLogo, desenhar, executar


class TestLogo(unittest.TestCase):
    def test_forward_norte(self):
        t = executar("FORWARD 3")
        self.assertEqual((t.x, t.y), (0, 3))

    def test_giros(self):
        t = executar("RT 90 FD 2 LT 180 FD 4")
        self.assertEqual((t.x, t.y, t.direcao), (-2, 0, 3))

    def test_quadrado_volta_ao_inicio(self):
        t = executar("REPEAT 4 [FD 3 RT 90]")
        self.assertEqual((t.x, t.y, t.direcao), (0, 0, 0))
        self.assertEqual(len(t.riscados), 12)

    def test_repeat_aninhado(self):
        t = executar("REPEAT 2 [REPEAT 3 [FD 1] RT 90]")
        self.assertEqual((t.x, t.y, t.direcao), (3, 3, 2))

    def test_caneta_levantada(self):
        t = executar("PU FD 5 PD FD 1")
        self.assertEqual(t.riscados, {(0, 0), (0, 6)})

    def test_back_home_comentario_minusculas(self):
        t = executar("fd 2 ; sobe\nbk 5\nhome")
        self.assertEqual((t.x, t.y), (0, 0))

    def test_desenho(self):
        t = executar("RT 90 FD 2")
        self.assertEqual(desenhar(t), "##@")

    def test_erros(self):
        invalidos = ["FD", "FD abc", "FD -1", "PULAR 3", "REPEAT 2 FD 1", "REPEAT 2 [FD 1",
                     "FD 1 ]", "RT 45", "REPEAT [FD 1]"]
        for prog in invalidos:
            with self.assertRaises(ErroLogo, msg=prog):
                executar(prog)

    def test_limite(self):
        with self.assertRaises(ErroLogo):
            executar("REPEAT 1000 [REPEAT 1000 [FD 1]]", limite=5000)


if __name__ == "__main__":
    unittest.main()
