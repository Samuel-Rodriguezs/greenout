import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_ordenacao_externa import OrdenadorExterno, ordenar_externo


class TestOrdenacaoExterna(unittest.TestCase):
    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            OrdenadorExterno(tam_run=0)
        with self.assertRaises(ValueError):
            OrdenadorExterno(fan_in=1)

    def test_vazio_e_unitario(self):
        self.assertEqual(ordenar_externo([]), [])
        self.assertEqual(ordenar_externo([5], tam_run=1), [5])

    def test_cabe_na_memoria_sem_disco(self):
        o = OrdenadorExterno(tam_run=100)
        self.assertEqual(list(o.ordenar([3, 1, 2])), [1, 2, 3])
        self.assertEqual(o.runs_criados, 0)

    def test_muitos_runs_uma_passada(self):
        rnd = random.Random(1)
        dados = [rnd.randrange(1000) for _ in range(500)]
        o = OrdenadorExterno(tam_run=100, fan_in=8)
        self.assertEqual(list(o.ordenar(dados)), sorted(dados))
        self.assertEqual(o.runs_criados, 5)
        self.assertEqual(o.passadas, 1)

    def test_varias_passadas_de_mesclagem(self):
        rnd = random.Random(2)
        dados = [rnd.random() for _ in range(1000)]
        o = OrdenadorExterno(tam_run=10, fan_in=3)
        self.assertEqual(list(o.ordenar(dados)), sorted(dados))
        self.assertGreater(o.passadas, 2)

    def test_ultimo_run_parcial(self):
        dados = list(range(25, 0, -1))
        self.assertEqual(ordenar_externo(dados, tam_run=10, fan_in=2), sorted(dados))

    def test_decrescente_e_chave_composta(self):
        linhas = [("a", 3), ("b", 1), ("a", 1), ("c", 2), ("b", 5)] * 7
        r = ordenar_externo(linhas, tam_run=4, fan_in=3, chave=lambda l: l[0], decrescente=True)
        self.assertEqual([l[0] for l in r], sorted((l[0] for l in linhas), reverse=True))
        r = ordenar_externo(linhas, tam_run=4, fan_in=3, chave=lambda l: (l[0], -l[1]))
        self.assertEqual(r, sorted(linhas, key=lambda l: (l[0], -l[1])))

    def test_estabilidade(self):
        linhas = [(i % 3, i) for i in range(60)]
        r = ordenar_externo(linhas, tam_run=7, fan_in=3, chave=lambda l: l[0])
        self.assertEqual(r, sorted(linhas, key=lambda l: l[0]))

    def test_estabilidade_decrescente(self):
        linhas = [(i % 3, i) for i in range(40)]
        r = ordenar_externo(linhas, tam_run=6, fan_in=2, chave=lambda l: l[0], decrescente=True)
        self.assertEqual(r, sorted(linhas, key=lambda l: l[0], reverse=True))

    def test_aceita_gerador_e_linhas_com_none(self):
        gen = ((None if i % 5 == 0 else i, "x") for i in range(50))
        r = ordenar_externo(gen, tam_run=9, fan_in=4, chave=lambda l: (l[0] is not None, l[0] or 0))
        self.assertEqual([l[0] for l in r][:10], [None] * 10)

    def test_limpa_arquivos_temporarios(self):
        with tempfile.TemporaryDirectory() as base:
            o = OrdenadorExterno(tam_run=5, fan_in=2, diretorio=base)
            self.assertEqual(list(o.ordenar(range(50, 0, -1))), list(range(1, 51)))
            self.assertEqual(os.listdir(base), [])

    def test_limpa_mesmo_com_abandono_ou_erro(self):
        with tempfile.TemporaryDirectory() as base:
            o = OrdenadorExterno(tam_run=5, fan_in=2, diretorio=base)
            g = o.ordenar(range(50, 0, -1))
            next(g)
            self.assertNotEqual(os.listdir(base), [])  # em uso durante a iteração
            g.close()
            self.assertEqual(os.listdir(base), [])
            with self.assertRaises(TypeError):
                list(OrdenadorExterno(tam_run=2, diretorio=base).ordenar([1, "a", 2, 3, 4]))
            self.assertEqual(os.listdir(base), [])


if __name__ == "__main__":
    unittest.main()
