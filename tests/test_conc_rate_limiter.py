import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_rate_limiter import RateLimiter


class RelogioFalso:
    def __init__(self):
        self.t = 0.0
        self.sonos = []

    def __call__(self):
        return self.t

    async def dormir(self, s):
        self.sonos.append(s)
        self.t += s


class TestRateLimiter(unittest.TestCase):
    def test_rajada_inicial(self):
        r = RelogioFalso()
        rl = RateLimiter(1, 3, r, r.dormir)
        self.assertEqual([rl.tentar() for _ in range(4)], [True, True, True, False])

    def test_reposicao_com_tempo(self):
        r = RelogioFalso()
        rl = RateLimiter(2, 2, r, r.dormir)
        rl.tentar(2)
        self.assertFalse(rl.tentar())
        r.t += 0.5  # 1 token
        self.assertTrue(rl.tentar())
        self.assertFalse(rl.tentar())

    def test_nao_excede_capacidade(self):
        r = RelogioFalso()
        rl = RateLimiter(10, 2, r, r.dormir)
        r.t += 100
        self.assertTrue(rl.tentar(2))
        self.assertFalse(rl.tentar())

    def test_adquirir_dorme_o_necessario(self):
        r = RelogioFalso()
        rl = RateLimiter(4, 1, r, r.dormir)

        async def main():
            esperas = [await rl.adquirir() for _ in range(3)]
            return esperas

        esperas = asyncio.run(main())
        self.assertEqual(esperas, [0.0, 0.25, 0.25])
        self.assertAlmostEqual(r.t, 0.5)

    def test_concorrentes_sao_espacados(self):
        r = RelogioFalso()
        rl = RateLimiter(1, 1, r, r.dormir)
        marcas = []

        async def uso():
            await rl.adquirir()
            marcas.append(r.t)

        async def main():
            await asyncio.gather(*(uso() for _ in range(4)))

        asyncio.run(main())
        self.assertEqual(marcas, [0.0, 1.0, 2.0, 3.0])

    def test_tempo_ate_disponivel(self):
        r = RelogioFalso()
        rl = RateLimiter(2, 1, r, r.dormir)
        rl.tentar()
        self.assertAlmostEqual(rl.tempo_ate_disponivel(), 0.5)

    def test_invalidos(self):
        with self.assertRaises(ValueError):
            RateLimiter(0)
        rl = RateLimiter(1, 1)
        with self.assertRaises(ValueError):
            asyncio.run(rl.adquirir(2))


if __name__ == "__main__":
    unittest.main()
