import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_dns import (TIPO_A, TIPO_AAAA, TIPO_CNAME, TIPO_NS, TIPO_TXT, Mensagem,
                      Pergunta, Registro, codificar_nome, consulta,
                      decodificar_nome, parse, serializar)


class TestRedeDns(unittest.TestCase):
    def test_consulta_vetor(self):
        esperado = "123401000001000000000000" "076578616d706c6503636f6d00" "00010001"
        self.assertEqual(consulta(0x1234, "example.com").hex(), esperado)

    def test_nome(self):
        self.assertEqual(codificar_nome("www.a.br"), b"\x03www\x01a\x02br\x00")
        self.assertEqual(codificar_nome("."), b"\x00")
        self.assertEqual(codificar_nome("a.br."), b"\x01a\x02br\x00")
        with self.assertRaises(ValueError):
            codificar_nome("a..b")
        with self.assertRaises(ValueError):
            codificar_nome("x" * 64 + ".com")

    def test_compressao_ponteiro(self):
        buf = bytearray(b"\x00" * 12)
        tab: dict[str, int] = {}
        buf += codificar_nome("www.example.com", buf, tab)
        buf += codificar_nome("mail.example.com", buf, tab)
        self.assertEqual(buf[12:].hex(), "03777777" "076578616d706c65" "03636f6d00"
                                          "046d61696c" "c010")
        nome, fim = decodificar_nome(bytes(buf), 12 + 17 + 0)
        self.assertEqual((nome, fim), ("mail.example.com", len(buf)))

    def test_ida_e_volta_resposta(self):
        m = Mensagem(
            0xBEEF, 0x8180,
            [Pergunta("www.exemplo.com.br", TIPO_A)],
            [Registro("www.exemplo.com.br", TIPO_CNAME, 300, "web.exemplo.com.br"),
             Registro("web.exemplo.com.br", TIPO_A, 60, bytes([192, 0, 2, 7])),
             Registro("web.exemplo.com.br", TIPO_AAAA, 60, bytes(15) + b"\x01")],
            [Registro("exemplo.com.br", TIPO_NS, 3600, "ns1.exemplo.com.br")],
            [Registro("ns1.exemplo.com.br", TIPO_TXT, 5, "v=spf1 -all")],
        )
        for comprimir in (True, False):
            r = parse(serializar(m, comprimir))
            self.assertEqual(r, m)
        self.assertLess(len(serializar(m, True)), len(serializar(m, False)))
        self.assertTrue(m.eh_resposta)
        self.assertEqual(m.rcode, 0)

    def test_rcode_nxdomain(self):
        self.assertEqual(Mensagem(1, 0x8183).rcode, 3)

    def test_txt_longo(self):
        txt = "a" * 300
        r = parse(serializar(Mensagem(1, 0x8000, [], [Registro("t.com", TIPO_TXT, 1, txt)])))
        self.assertEqual(r.respostas[0].dados, txt)

    def test_laco_de_ponteiros(self):
        msg = b"\x00" * 12 + b"\xc0\x0c"  # aponta para si mesmo
        with self.assertRaises(ValueError):
            decodificar_nome(msg, 12)

    def test_truncados(self):
        valido = consulta(1, "example.com")
        for n in (5, 11, 14, len(valido) - 1):
            with self.assertRaises(ValueError, msg=str(n)):
                parse(valido[:n])
        with self.assertRaises(ValueError):
            decodificar_nome(b"\x05ab", 0)

    def test_maiusculas_comprimem_igual(self):
        m = Mensagem(1, 0, [Pergunta("Example.COM")], [Registro("example.com", TIPO_A, 1, b"\x01\x02\x03\x04")])
        raw = serializar(m)
        self.assertIn(b"\xc0\x0c", raw)


if __name__ == "__main__":
    unittest.main()
