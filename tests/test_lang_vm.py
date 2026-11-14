import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_vm import (ADD, CALL, DIV, DUP, ErroVM, GT, HALT, JMP, JNZ, JZ, LOAD, MUL, POP,
                     PRINT, PUSH, RET, STORE, SUB, SWAP, executar)


class TestVM(unittest.TestCase):
    def test_aritmetica(self):
        prog = [(PUSH, 2), (PUSH, 3), (ADD, None), (PUSH, 4), (MUL, None), (PRINT, None)]
        self.assertEqual(executar(prog), [20])

    def test_sub_swap_dup(self):
        prog = [(PUSH, 1), (PUSH, 5), (SWAP, None), (SUB, None), (DUP, None), (PRINT, None), (PRINT, None)]
        self.assertEqual(executar(prog), [4, 4])

    def test_contagem_regressiva(self):
        prog = [
            (PUSH, 3), (STORE, 0),
            (LOAD, 0), (PRINT, None),       # 2,3
            (LOAD, 0), (PUSH, 1), (SUB, None), (DUP, None), (STORE, 0),  # 4..8
            (JNZ, 2), (HALT, None),
        ]
        self.assertEqual(executar(prog), [3, 2, 1])

    def test_jz_e_jmp(self):
        prog = [(PUSH, 0), (JZ, 3), (PUSH, 99), (PUSH, 7), (PRINT, None)]
        self.assertEqual(executar(prog), [7])
        self.assertEqual(executar([(JMP, 2), (PUSH, 1), (PUSH, 2), (PRINT, None)]), [2])

    def test_call_ret(self):
        prog = [(CALL, 3), (PRINT, None), (HALT, None), (PUSH, 42), (RET, None)]
        self.assertEqual(executar(prog), [42])

    def test_comparacao(self):
        self.assertEqual(executar([(PUSH, 5), (PUSH, 2), (GT, None), (PRINT, None)]), [1])

    def test_divisao_por_zero(self):
        with self.assertRaises(ErroVM):
            executar([(PUSH, 1), (PUSH, 0), (DIV, None)])

    def test_pilha_vazia(self):
        with self.assertRaises(ErroVM):
            executar([(POP, None)])

    def test_opcode_invalido_e_salto_invalido(self):
        with self.assertRaises(ErroVM):
            executar([(99, None)])
        with self.assertRaises(ErroVM):
            executar([(JMP, 50)])

    def test_ret_sem_call_e_laco_infinito(self):
        with self.assertRaises(ErroVM):
            executar([(RET, None)])
        with self.assertRaises(ErroVM):
            executar([(JMP, 0)])


if __name__ == "__main__":
    unittest.main()
