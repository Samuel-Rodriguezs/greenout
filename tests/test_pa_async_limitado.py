import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from pa_async_limitado import executar_limitado


class TestAsyncLimitado(unittest.TestCase):
    def test_resultados_em_ordem(self):
        async def f(x):
            await asyncio.sleep(0.01 * (5 - x))
            return x * 10

        r = asyncio.run(executar_limitado(range(5), f, limite=5))
        self.assertEqual(r, [0, 10, 20, 30, 40])

    def test_respeita_limite(self):
        ativos = {"n": 0, "max": 0}

        async def f(x):
            ativos["n"] += 1
            ativos["max"] = max(ativos["max"], ativos["n"])
            await asyncio.sleep(0.01)
            ativos["n"] -= 1
            return x

        asyncio.run(executar_limitado(range(10), f, limite=3))
        self.assertEqual(ativos["max"], 3)

    def test_timeout_e_erro_viram_excecoes(self):
        async def f(x):
            if x == 1:
                await asyncio.sleep(1)
            if x == 2:
                raise KeyError("k")
            return x

        r = asyncio.run(executar_limitado([0, 1, 2], f, limite=3, timeout=0.05))
        self.assertEqual(r[0], 0)
        self.assertIsInstance(r[1], asyncio.TimeoutError)
        self.assertIsInstance(r[2], KeyError)

    def test_vazio(self):
        async def f(x):
            return x

        self.assertEqual(asyncio.run(executar_limitado([], f)), [])

    def test_limite_invalido(self):
        async def f(x):
            return x

        with self.assertRaises(ValueError):
            asyncio.run(executar_limitado([1], f, limite=0))


if __name__ == "__main__":
    unittest.main()
