import sys
import unittest
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from uni_grep import filtrar, main

TEXTO = "Gato\ncachorro\ngato preto\n"


class TestUniGrep(unittest.TestCase):
    def test_filtrar_basico(self):
        self.assertEqual(filtrar(TEXTO.splitlines(), "gato"), [(3, "gato preto")])

    def test_ignorar_caixa(self):
        self.assertEqual([i for i, _ in filtrar(TEXTO.splitlines(), "gato", True)], [1, 3])

    def test_inverter(self):
        self.assertEqual(filtrar(TEXTO.splitlines(), "gato", True, True), [(2, "cachorro")])

    def test_regex(self):
        self.assertEqual(len(filtrar(["a1", "b", "c22"], r"\d+$")), 2)

    def test_main_numerado(self):
        s = StringIO()
        self.assertEqual(main(["-n", "gato"], TEXTO, s), 0)
        self.assertEqual(s.getvalue(), "3:gato preto\n")

    def test_main_contagem(self):
        s = StringIO()
        main(["-ic", "gato"], TEXTO, s)
        self.assertEqual(s.getvalue(), "2\n")

    def test_sem_correspondencia(self):
        self.assertEqual(main(["zzz"], TEXTO, StringIO()), 1)

    def test_regex_invalida(self):
        self.assertEqual(main(["("], TEXTO, StringIO()), 2)

    def test_sem_padrao(self):
        self.assertEqual(main([], TEXTO, StringIO()), 2)

    def test_opcao_invalida(self):
        self.assertEqual(main(["-z", "a"], TEXTO, StringIO()), 2)

    def test_arquivo_inexistente(self):
        self.assertEqual(main(["a", "/nao/existe/xyz"], "", StringIO()), 2)


if __name__ == "__main__":
    unittest.main()
