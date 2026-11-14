import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "python"))

from ed_heap_minimo import HeapMinimo, heap_sort


class TestHeapMinimo(unittest.TestCase):
    def test_vazio(self) -> None:
        heap = HeapMinimo()
        self.assertTrue(heap.vazio())
        with self.assertRaises(IndexError):
            heap.minimo()
        with self.assertRaises(IndexError):
            heap.extrair()

    def test_minimo_apos_insercoes(self) -> None:
        heap = HeapMinimo()
        for v in (5, 3, 8, 1):
            heap.inserir(v)
        self.assertEqual(heap.minimo(), 1)
        self.assertEqual(len(heap), 4)

    def test_extrair_em_ordem(self) -> None:
        heap = HeapMinimo([9, 4, 7, 1, 8, 2])
        self.assertEqual([heap.extrair() for _ in range(6)], [1, 2, 4, 7, 8, 9])

    def test_duplicados_e_negativos(self) -> None:
        self.assertEqual(heap_sort([3, -1, 3, 0, -1]), [-1, -1, 0, 3, 3])

    def test_um_elemento(self) -> None:
        heap = HeapMinimo([7])
        self.assertEqual(heap.extrair(), 7)
        self.assertTrue(heap.vazio())

    def test_heap_sort_vazio(self) -> None:
        self.assertEqual(heap_sort([]), [])


if __name__ == "__main__":
    unittest.main()
