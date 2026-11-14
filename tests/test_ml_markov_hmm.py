import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from ml_markov_hmm import HMM, CadeiaMarkov

CLIMA = CadeiaMarkov(["sol", "chuva"],
                     {"sol": {"sol": 0.9, "chuva": 0.1}, "chuva": {"sol": 0.5, "chuva": 0.5}})

# exemplo clássico: saudável/febre; normal/frio/tonto
HMM_MED = HMM(
    ["Saudavel", "Febre"],
    {"Saudavel": 0.6, "Febre": 0.4},
    {"Saudavel": {"Saudavel": 0.7, "Febre": 0.3}, "Febre": {"Saudavel": 0.4, "Febre": 0.6}},
    {"Saudavel": {"normal": 0.5, "frio": 0.4, "tonto": 0.1},
     "Febre": {"normal": 0.1, "frio": 0.3, "tonto": 0.6}},
)


class TestMarkov(unittest.TestCase):
    def test_prob_sequencia(self):
        self.assertAlmostEqual(CLIMA.prob_sequencia(["sol", "sol", "chuva"]), 0.5 * 0.9 * 0.1)

    def test_estacionaria(self):
        d = CLIMA.distribuicao_estacionaria()
        self.assertAlmostEqual(d["sol"], 5 / 6, places=6)
        self.assertAlmostEqual(sum(d.values()), 1.0)

    def test_linha_invalida(self):
        with self.assertRaises(ValueError):
            CadeiaMarkov(["a", "b"], {"a": {"a": 0.5, "b": 0.4}, "b": {"a": 1.0}})

    def test_estimar(self):
        c = CadeiaMarkov.estimar([["a", "b"] * 50], ["a", "b"])
        self.assertGreater(c.transicao["a"]["b"], 0.95)

    def test_viterbi_classico(self):
        caminho, p = HMM_MED.viterbi(["normal", "frio", "tonto"])
        self.assertEqual(caminho, ["Saudavel", "Saudavel", "Febre"])
        self.assertAlmostEqual(p, 0.01512)

    def test_forward_maior_que_viterbi(self):
        obs = ["normal", "frio", "tonto"]
        self.assertGreaterEqual(HMM_MED.forward(obs), HMM_MED.viterbi(obs)[1])

    def test_forward_soma_um_sobre_observacoes(self):
        simbolos = ["normal", "frio", "tonto"]
        total = sum(HMM_MED.forward([a, b]) for a in simbolos for b in simbolos)
        self.assertAlmostEqual(total, 1.0)

    def test_uma_observacao(self):
        caminho, _ = HMM_MED.viterbi(["tonto"])
        self.assertEqual(caminho, ["Febre"])

    def test_vazio(self):
        with self.assertRaises(ValueError):
            HMM_MED.viterbi([])
        with self.assertRaises(ValueError):
            HMM_MED.forward([])


if __name__ == "__main__":
    unittest.main()
