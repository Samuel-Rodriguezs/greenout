import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from lang_assembler import ErroAssembler, desmontar, montar
from lang_vm import PUSH, executar

FATORIAL = """
    push 5
    store 0        ; n
    push 1
    store 1        ; acc
laco:
    load 0
    jz fim
    load 1
    load 0
    mul
    store 1
    load 0
    push 1
    sub
    store 0
    jmp laco
fim:
    load 1
    print
    halt
"""


class TestAssembler(unittest.TestCase):
    def test_fatorial(self):
        self.assertEqual(executar(montar(FATORIAL)), [120])

    def test_montagem_basica(self):
        self.assertEqual(montar("PUSH 3"), [(PUSH, 3)])

    def test_rotulo_na_mesma_linha(self):
        prog = montar("inicio: push 1\nprint")
        self.assertEqual(executar(prog), [1])

    def test_ida_e_volta(self):
        prog = montar(FATORIAL)
        self.assertEqual(montar(desmontar(prog)), prog)

    def test_instrucao_desconhecida(self):
        with self.assertRaises(ErroAssembler):
            montar("FOO 1")

    def test_argumento_faltando_ou_sobrando(self):
        with self.assertRaises(ErroAssembler):
            montar("PUSH")
        with self.assertRaises(ErroAssembler):
            montar("ADD 1")

    def test_argumento_nao_numerico(self):
        with self.assertRaises(ErroAssembler):
            montar("PUSH abc")

    def test_rotulo_indefinido_e_duplicado(self):
        with self.assertRaises(ErroAssembler):
            montar("JMP nada")
        with self.assertRaises(ErroAssembler):
            montar("a:\na:\nHALT")


if __name__ == "__main__":
    unittest.main()
