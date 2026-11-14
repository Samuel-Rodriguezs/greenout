import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from bd_serial_linhas import (INT_MAX, INT_MIN, ErroSerializacaoLinha,
                              codificar_linha, decodificar_linha)

ESQ = [("id", "INT"), ("nome", "TEXT"), ("nota", "REAL"), ("ativo", "BOOL")]


class TestSerialLinhas(unittest.TestCase):
    def test_ida_e_volta(self):
        linha = [42, "João ção", 7.25, True]
        self.assertEqual(decodificar_linha(ESQ, codificar_linha(ESQ, linha)), linha)

    def test_nulos_em_qualquer_posicao(self):
        for linha in ([None] * 4, [1, None, None, False], [None, "x", 1.0, None]):
            self.assertEqual(decodificar_linha(ESQ, codificar_linha(ESQ, linha)), linha)

    def test_nulos_ocupam_so_o_bitmap(self):
        self.assertEqual(len(codificar_linha(ESQ, [None] * 4)), 1)

    def test_bitmap_com_mais_de_8_colunas(self):
        esq = [(f"c{i}", "INT") for i in range(10)]
        linha = [i if i % 3 else None for i in range(10)]
        dados = codificar_linha(esq, linha)
        self.assertEqual(decodificar_linha(esq, dados), linha)

    def test_limites_de_inteiro(self):
        esq = [("a", "INT"), ("b", "INT")]
        self.assertEqual(decodificar_linha(esq, codificar_linha(esq, [INT_MIN, INT_MAX])), [INT_MIN, INT_MAX])
        with self.assertRaises(ErroSerializacaoLinha):
            codificar_linha(esq, [INT_MAX + 1, 0])

    def test_real_aceita_int_e_texto_vazio(self):
        esq = [("r", "REAL"), ("t", "TEXT")]
        self.assertEqual(decodificar_linha(esq, codificar_linha(esq, [3, ""])), [3.0, ""])

    def test_tipos_errados(self):
        casos = [[True, "a", 1.0, True], ["1", "a", 1.0, True], [1, 5, 1.0, True],
                 [1, "a", "x", True], [1, "a", 1.0, 1], [1, "a", True, True]]
        for c in casos:
            with self.assertRaises(ErroSerializacaoLinha, msg=str(c)):
                codificar_linha(ESQ, c)

    def test_aridade(self):
        with self.assertRaises(ErroSerializacaoLinha):
            codificar_linha(ESQ, [1])

    def test_esquema_invalido(self):
        with self.assertRaises(ErroSerializacaoLinha):
            codificar_linha([("a", "BLOB")], [1])
        with self.assertRaises(ErroSerializacaoLinha):
            codificar_linha([("a", "INT"), ("a", "INT")], [1, 2])

    def test_dados_truncados_em_todo_ponto(self):
        dados = codificar_linha(ESQ, [1, "abc", 2.5, True])
        for n in range(len(dados)):
            with self.assertRaises(ErroSerializacaoLinha, msg=f"n={n}"):
                decodificar_linha(ESQ, dados[:n])

    def test_bytes_sobrando(self):
        dados = codificar_linha(ESQ, [1, "a", 1.0, True]) + b"\x00"
        with self.assertRaises(ErroSerializacaoLinha):
            decodificar_linha(ESQ, dados)

    def test_booleano_e_utf8_corrompidos(self):
        esq = [("b", "BOOL")]
        with self.assertRaises(ErroSerializacaoLinha):
            decodificar_linha(esq, b"\x00\x07")
        esq = [("t", "TEXT")]
        with self.assertRaises(ErroSerializacaoLinha):
            decodificar_linha(esq, b"\x00" + b"\x01\x00\x00\x00" + b"\xff")

    def test_tamanho_de_texto_absurdo(self):
        with self.assertRaises(ErroSerializacaoLinha):
            decodificar_linha([("t", "TEXT")], b"\x00" + b"\xff\xff\xff\x7f" + b"ab")


if __name__ == "__main__":
    unittest.main()
