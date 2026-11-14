import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from so_tabela_paginas import MMU, TLB, FaltaDePagina, dividir, tempo_efetivo_acesso


class TestTabelaPaginas(unittest.TestCase):
    def test_dividir(self):
        va = (1 << 22) | (2 << 12) | 0x34
        self.assertEqual(dividir(va), (1, 2, 0x34))
        self.assertEqual(dividir(0xFFFFFFFF), (1023, 1023, 4095))
        with self.assertRaises(ValueError):
            dividir(1 << 32)

    def test_traducao(self):
        mmu = MMU()
        mmu.mapear((1 << 10) | 2, 5)
        self.assertEqual(mmu.traduzir((1 << 22) | (2 << 12) | 0x34), 5 * 4096 + 0x34)

    def test_falta_de_pagina_nos_dois_niveis(self):
        mmu = MMU()
        mmu.mapear(2, 7)
        with self.assertRaises(FaltaDePagina):  # diretório inexistente
            mmu.traduzir(5 << 22)
        with self.assertRaises(FaltaDePagina):  # diretório existe, página não
            mmu.traduzir(3 << 12)
        self.assertEqual(mmu.tlb.vpns(), [])

    def test_tabelas_esparsas(self):
        mmu = MMU()
        mmu.mapear(0, 1)
        mmu.mapear(1, 2)  # mesmo diretório
        self.assertEqual(mmu.tabelas_alocadas, 2)
        mmu.mapear(1 << 10, 3)  # outro diretório
        self.assertEqual(mmu.tabelas_alocadas, 3)
        mmu.desmapear(1 << 10)
        self.assertEqual(mmu.tabelas_alocadas, 2)
        with self.assertRaises(KeyError):
            mmu.desmapear(99)

    def test_tlb_lru_e_taxa_de_acerto(self):
        mmu = MMU(tlb_capacidade=2)
        for vpn in (10, 11, 12):
            mmu.mapear(vpn, vpn + 100)
        A, B, C = (10 << 12), (11 << 12), (12 << 12)
        for va in (A, B, A, C, B):  # M M H M(evict B) M
            mmu.traduzir(va)
        self.assertEqual((mmu.tlb.acertos, mmu.tlb.faltas), (1, 4))
        self.assertAlmostEqual(mmu.tlb.taxa_acerto, 0.2)
        self.assertEqual(mmu.tlb.vpns(), [12, 11])
        self.assertEqual(mmu.acessos_tabela, 8)  # 4 faltas x 2 níveis

    def test_remapear_invalida_tlb(self):
        mmu = MMU()
        mmu.mapear(1, 9)
        self.assertEqual(mmu.traduzir(1 << 12), 9 * 4096)
        mmu.mapear(1, 4)
        self.assertEqual(mmu.traduzir(1 << 12), 4 * 4096)

    def test_tempo_efetivo(self):
        self.assertAlmostEqual(tempo_efetivo_acesso(0.8, 20, 100, niveis=1), 140.0)
        self.assertAlmostEqual(tempo_efetivo_acesso(0.8, 20, 100, niveis=2), 160.0)
        self.assertAlmostEqual(tempo_efetivo_acesso(1.0, 20, 100), 120.0)
        with self.assertRaises(ValueError):
            tempo_efetivo_acesso(1.5, 1, 1)

    def test_tlb_capacidade_invalida(self):
        with self.assertRaises(ValueError):
            TLB(0)


if __name__ == "__main__":
    unittest.main()
