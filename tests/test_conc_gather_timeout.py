import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from conc_gather_timeout import gather_com_timeout


async def rapido(v):
    await asyncio.sleep(0)
    return v


async def travado(sinal=None):
    try:
        await asyncio.Event().wait()  # nunca liberado
    except asyncio.CancelledError:
        if sinal is not None:
            sinal.append("cancelada")
        raise


async def quebra():
    await asyncio.sleep(0)
    raise ValueError("erro")


class TestGatherTimeout(unittest.TestCase):
    def test_todas_completam(self):
        r = asyncio.run(gather_com_timeout([rapido(1), rapido(2)], 1))
        self.assertEqual(r.resultados, [1, 2])
        self.assertTrue(r.completo)

    def test_timeout_cancela_pendentes(self):
        sinal = []

        async def main():
            return await gather_com_timeout([rapido("a"), travado(sinal), rapido("c")], 0.02)

        r = asyncio.run(main())
        self.assertEqual(r.concluidas, [0, 2])
        self.assertEqual(r.canceladas, [1])
        self.assertEqual(r.resultados, ["a", None, "c"])
        self.assertEqual(sinal, ["cancelada"])
        self.assertFalse(r.completo)

    def test_excecoes_coletadas(self):
        r = asyncio.run(gather_com_timeout([rapido(1), quebra()], 1))
        self.assertEqual(r.falhas, [1])
        self.assertIsInstance(r.resultados[1], ValueError)
        self.assertEqual(r.concluidas, [0])

    def test_falhar_rapido_cancela_restantes(self):
        sinal = []
        r = asyncio.run(gather_com_timeout([quebra(), travado(sinal)], 5, falhar_rapido=True))
        self.assertEqual(r.falhas, [0])
        self.assertEqual(r.canceladas, [1])
        self.assertEqual(sinal, ["cancelada"])

    def test_vazio(self):
        r = asyncio.run(gather_com_timeout([], 1))
        self.assertEqual(r.resultados, [])
        self.assertTrue(r.completo)

    def test_sem_tarefas_vazando(self):
        async def main():
            await gather_com_timeout([travado(), travado()], 0.01)
            atuais = asyncio.all_tasks() - {asyncio.current_task()}
            return len(atuais)

        self.assertEqual(asyncio.run(main()), 0)


if __name__ == "__main__":
    unittest.main()
