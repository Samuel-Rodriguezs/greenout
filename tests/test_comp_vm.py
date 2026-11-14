import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from comp_vm import (ErroExecucao, FuncaoVM, Instr, Op, ProgramaVM, desmontar,
                     executar)


def I(op, arg=None):
    return Instr(op, arg)


def prog(codigo, n_locais=0, funcoes=()):
    return ProgramaVM(list(funcoes), FuncaoVM("main", 0, n_locais, codigo))


class TestVM(unittest.TestCase):
    def test_aritmetica_e_print(self):
        # print((2 + 3) * 4)
        r = executar(prog([I(Op.PUSH, 2), I(Op.PUSH, 3), I(Op.ADD), I(Op.PUSH, 4),
                           I(Op.MUL), I(Op.PRINT), I(Op.HALT)]))
        self.assertEqual(r.saida, ["20"])

    def test_ordem_dos_operandos(self):
        r = executar(prog([I(Op.PUSH, 10), I(Op.PUSH, 3), I(Op.SUB), I(Op.PRINT),
                           I(Op.PUSH, -7), I(Op.PUSH, 2), I(Op.DIV), I(Op.PRINT),
                           I(Op.PUSH, -7), I(Op.PUSH, 2), I(Op.MOD), I(Op.PRINT), I(Op.HALT)]))
        self.assertEqual(r.saida, ["7", "-3", "-1"])

    def test_booleanos_impressos(self):
        r = executar(prog([I(Op.PUSH, 1), I(Op.PUSH, 2), I(Op.LT), I(Op.PRINT),
                           I(Op.PUSH, True), I(Op.NOT), I(Op.PRINT), I(Op.HALT)]))
        self.assertEqual(r.saida, ["true", "false"])

    def test_locais(self):
        r = executar(prog([I(Op.PUSH, 5), I(Op.STORE, 0), I(Op.LOAD, 0), I(Op.LOAD, 0),
                           I(Op.MUL), I(Op.STORE, 1), I(Op.HALT)], n_locais=2))
        self.assertEqual(r.locais, [5, 25])

    def test_loop_com_saltos(self):
        # i = 0; while (i < 3) { print(i); i = i + 1; }
        codigo = [I(Op.PUSH, 0), I(Op.STORE, 0),
                  I(Op.LOAD, 0), I(Op.PUSH, 3), I(Op.LT), I(Op.JZ, 13),
                  I(Op.LOAD, 0), I(Op.PRINT),
                  I(Op.LOAD, 0), I(Op.PUSH, 1), I(Op.ADD), I(Op.STORE, 0),
                  I(Op.JMP, 2), I(Op.HALT)]
        r = executar(prog(codigo, 1))
        self.assertEqual(r.saida, ["0", "1", "2"])

    def test_dup_e_jz(self):
        r = executar(prog([I(Op.PUSH, False), I(Op.DUP), I(Op.JZ, 4), I(Op.POP),
                           I(Op.PRINT), I(Op.HALT)]))
        self.assertEqual(r.saida, ["false"])

    def test_chamada_e_retorno(self):
        # func dobro(a) { return a + a; }  print(dobro(21));
        dobro = FuncaoVM("dobro", 1, 1, [I(Op.LOAD, 0), I(Op.LOAD, 0), I(Op.ADD), I(Op.RET)])
        r = executar(prog([I(Op.PUSH, 21), I(Op.CALL, 0), I(Op.PRINT), I(Op.HALT)],
                          funcoes=[dobro]))
        self.assertEqual(r.saida, ["42"])

    def test_ordem_dos_argumentos(self):
        sub = FuncaoVM("sub", 2, 2, [I(Op.LOAD, 0), I(Op.LOAD, 1), I(Op.SUB), I(Op.RET)])
        r = executar(prog([I(Op.PUSH, 9), I(Op.PUSH, 4), I(Op.CALL, 0), I(Op.PRINT),
                           I(Op.HALT)], funcoes=[sub]))
        self.assertEqual(r.saida, ["5"])

    def test_recursao(self):
        # func fat(n) { if (n <= 1) return 1; return n * fat(n - 1); }
        fat = FuncaoVM("fat", 1, 1, [
            I(Op.LOAD, 0), I(Op.PUSH, 1), I(Op.LE), I(Op.JZ, 6),
            I(Op.PUSH, 1), I(Op.RET),
            I(Op.LOAD, 0), I(Op.LOAD, 0), I(Op.PUSH, 1), I(Op.SUB), I(Op.CALL, 0),
            I(Op.MUL), I(Op.RET)])
        r = executar(prog([I(Op.PUSH, 10), I(Op.CALL, 0), I(Op.PRINT), I(Op.HALT)],
                          funcoes=[fat]))
        self.assertEqual(r.saida, ["3628800"])

    def test_divisao_por_zero(self):
        with self.assertRaisesRegex(ErroExecucao, "divisão por zero"):
            executar(prog([I(Op.PUSH, 1), I(Op.PUSH, 0), I(Op.DIV), I(Op.HALT)]))

    def test_limite_de_passos(self):
        with self.assertRaisesRegex(ErroExecucao, "limite de passos"):
            executar(prog([I(Op.JMP, 0)]), max_passos=1000)

    def test_estouro_de_pilha_de_chamadas(self):
        f = FuncaoVM("f", 0, 0, [I(Op.CALL, 0), I(Op.RET)])
        with self.assertRaisesRegex(ErroExecucao, "pilha de chamadas"):
            executar(prog([I(Op.CALL, 0), I(Op.HALT)], funcoes=[f]), max_profundidade=50)

    def test_pilha_vazia(self):
        with self.assertRaisesRegex(ErroExecucao, "pilha vazia"):
            executar(prog([I(Op.ADD)]))

    def test_sair_do_fim(self):
        with self.assertRaisesRegex(ErroExecucao, "saiu do fim"):
            executar(prog([I(Op.PUSH, 1)]))

    def test_locais_iniciais(self):
        r = executar(prog([I(Op.LOAD, 0), I(Op.PRINT), I(Op.HALT)], 1), locais_iniciais={0: 77})
        self.assertEqual(r.saida, ["77"])

    def test_desmontar(self):
        txt = desmontar(prog([I(Op.PUSH, True), I(Op.JZ, 2), I(Op.HALT)]))
        self.assertIn("PUSH true", txt)
        self.assertIn("JZ 2", txt)
        self.assertTrue(txt.startswith("main"))


if __name__ == "__main__":
    unittest.main()
