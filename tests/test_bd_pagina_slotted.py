import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_pagina_slotted import PaginaCheia, PaginaSlotted


class TestPaginaSlotted(unittest.TestCase):
    def test_tamanho_invalido(self):
        with self.assertRaises(ValueError):
            PaginaSlotted(4)
        with self.assertRaises(ValueError):
            PaginaSlotted(70000)

    def test_inserir_e_ler(self):
        p = PaginaSlotted(256)
        a = p.inserir(b"ola")
        b = p.inserir(b"mundo cruel")
        self.assertEqual((a, b), (0, 1))
        self.assertEqual(p.ler(a), b"ola")
        self.assertEqual(p.ler(b), b"mundo cruel")
        self.assertEqual(p.n_slots, 2)

    def test_registro_vazio_rejeitado(self):
        with self.assertRaises(ValueError):
            PaginaSlotted(128).inserir(b"")

    def test_remocao_e_reuso_de_slot(self):
        p = PaginaSlotted(256)
        a, b, c = p.inserir(b"aaa"), p.inserir(b"bbb"), p.inserir(b"ccc")
        p.remover(b)
        with self.assertRaises(KeyError):
            p.ler(b)
        with self.assertRaises(KeyError):
            p.remover(b)
        self.assertEqual(p.inserir(b"novo"), b)
        self.assertEqual(p.ler(a), b"aaa")
        self.assertEqual(p.ler(c), b"ccc")
        self.assertEqual(p.n_slots, 3)

    def test_slot_inexistente(self):
        with self.assertRaises(IndexError):
            PaginaSlotted(128).ler(0)

    def test_pagina_cheia_e_compactacao_automatica(self):
        p = PaginaSlotted(128)
        slots = []
        while True:
            try:
                slots.append(p.inserir(b"x" * 20))
            except PaginaCheia:
                break
        self.assertGreaterEqual(len(slots), 4)
        for s in slots[::2]:
            p.remover(s)
        # há espaço fragmentado: só cabe após compactar
        novo = p.inserir(b"y" * 40)
        self.assertEqual(p.ler(novo), b"y" * 40)
        for s in slots[1::2]:
            self.assertEqual(p.ler(s), b"x" * 20)

    def test_atualizar_menor_igual_e_maior(self):
        p = PaginaSlotted(200)
        a = p.inserir(b"abcdef")
        b = p.inserir(b"zz")
        p.atualizar(a, b"abc")
        self.assertEqual(p.ler(a), b"abc")
        p.atualizar(a, b"0123456789" * 3)
        self.assertEqual(p.ler(a), b"0123456789" * 3)
        self.assertEqual(p.ler(b), b"zz")

    def test_atualizar_sem_espaco_preserva_original(self):
        p = PaginaSlotted(64)
        a = p.inserir(b"a" * 20)
        p.inserir(b"b" * 20)
        with self.assertRaises(PaginaCheia):
            p.atualizar(a, b"c" * 40)
        self.assertEqual(p.ler(a), b"a" * 20)

    def test_serializacao_ida_e_volta(self):
        p = PaginaSlotted(256)
        ids = [p.inserir(bytes([65 + i]) * (i + 1)) for i in range(5)]
        p.remover(ids[2])
        q = PaginaSlotted.de_bytes(p.para_bytes())
        self.assertEqual(list(q.registros()), list(p.registros()))
        self.assertEqual(len(q.para_bytes()), 256)

    def test_bytes_mortos(self):
        p = PaginaSlotted(256)
        a = p.inserir(b"a" * 10)
        p.inserir(b"b" * 5)
        self.assertEqual(p.bytes_mortos(), 0)
        p.remover(a)
        self.assertEqual(p.bytes_mortos(), 10)
        p.compactar()
        self.assertEqual(p.bytes_mortos(), 0)

    def test_bytes_corrompidos(self):
        bruto = bytearray(PaginaSlotted(64).para_bytes())
        bruto[0] = 200  # n_slots absurdo
        with self.assertRaises(ValueError):
            PaginaSlotted.de_bytes(bytes(bruto))


if __name__ == "__main__":
    unittest.main()
