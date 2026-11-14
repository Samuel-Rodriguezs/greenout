import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_retry_async import TentativasEsgotadas, atraso_backoff, com_retry


class Instavel:
    def __init__(self, falhas, exc=ConnectionError):
        self.falhas, self.exc, self.chamadas = falhas, exc, 0

    async def __call__(self):
        self.chamadas += 1
        if self.chamadas <= self.falhas:
            raise self.exc(f"falha {self.chamadas}")
        return "ok"


class TestRetryAsync(unittest.TestCase):
    def setUp(self):
        self.sonos = []

        async def dormir(s):
            self.sonos.append(s)

        self.dormir = dormir

    def test_sucesso_direto(self):
        fn = Instavel(0)
        r = asyncio.run(com_retry(fn, dormir=self.dormir))
        self.assertEqual((r, fn.chamadas, self.sonos), ("ok", 1, []))

    def test_backoff_exponencial(self):
        fn = Instavel(2)
        r = asyncio.run(com_retry(fn, tentativas=4, base=0.5, dormir=self.dormir))
        self.assertEqual(r, "ok")
        self.assertEqual(self.sonos, [0.5, 1.0])

    def test_esgota(self):
        fn = Instavel(10)
        with self.assertRaises(TentativasEsgotadas) as ctx:
            asyncio.run(com_retry(fn, tentativas=3, dormir=self.dormir))
        self.assertEqual(ctx.exception.tentativas, 3)
        self.assertEqual(fn.chamadas, 3)
        self.assertEqual(len(self.sonos), 2)  # não dorme após a última

    def test_excecao_nao_listada_propaga(self):
        fn = Instavel(5, exc=KeyError)
        with self.assertRaises(KeyError):
            asyncio.run(com_retry(fn, excecoes=(ConnectionError,), dormir=self.dormir))
        self.assertEqual(fn.chamadas, 1)

    def test_atraso_maximo(self):
        self.assertEqual(atraso_backoff(10, base=1, fator=2, maximo=5), 5)

    def test_jitter(self):
        self.assertEqual(atraso_backoff(1, base=2, jitter=lambda d: d / 2), 1.0)

    def test_tentativas_invalidas(self):
        with self.assertRaises(ValueError):
            asyncio.run(com_retry(Instavel(0), tentativas=0))


if __name__ == "__main__":
    unittest.main()
