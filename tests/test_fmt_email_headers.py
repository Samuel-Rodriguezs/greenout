import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fmt_email_headers import Endereco, ErroEmail, decodificar_palavra, parse_cabecalhos, parse_enderecos


class TestFmtEmailHeaders(unittest.TestCase):
    def test_cabecalhos_e_corpo(self):
        msg = "From: Ana <ana@ex.com>\r\nSubject: Olá\r\n mundo\r\nReceived: a\r\nReceived: b\r\n\r\nCorpo aqui\r\n"
        cab, corpo = parse_cabecalhos(msg)
        self.assertEqual(cab["subject"], ["Olá mundo"])
        self.assertEqual(cab["received"], ["a", "b"])
        self.assertEqual(corpo, "Corpo aqui\n")

    def test_so_cabecalhos(self):
        cab, corpo = parse_cabecalhos("To: x@y.com\n")
        self.assertEqual((cab["to"], corpo), (["x@y.com"], ""))

    def test_enderecos(self):
        r = parse_enderecos('Ana Silva <ana@ex.com>, bob@ex.org, "Souza, Carlos" <c@ex.com>, <d@localhost>')
        self.assertEqual(r, [Endereco("Ana Silva", "ana@ex.com"), Endereco("", "bob@ex.org"),
                             Endereco("Souza, Carlos", "c@ex.com"), Endereco("", "d@localhost")])

    def test_comentario_em_endereco(self):
        self.assertEqual(parse_enderecos("bob@ex.org (Bob)"), [Endereco("", "bob@ex.org")])

    def test_rfc2047(self):
        self.assertEqual(decodificar_palavra("=?UTF-8?B?w6dhZsOp?="), "çafé")
        self.assertEqual(decodificar_palavra("=?iso-8859-1?Q?caf=E9_ol=E1?= fim"), "café olá fim")
        self.assertEqual(decodificar_palavra("=?utf-8?Q?a?= =?utf-8?Q?b?="), "ab")

    def test_malformados(self):
        for ruim in ["", "sem dois pontos\n\ncorpo", " continuação\nA: b", "Nome Com Espaço: x"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroEmail):
                    parse_cabecalhos(ruim)
        for ruim in ["não é email", "<a@b.com", '"Aberto <a@b.com>', "Ana <sem-arroba>"]:
            with self.subTest(ruim=ruim):
                with self.assertRaises(ErroEmail):
                    parse_enderecos(ruim)
        with self.assertRaises(ErroEmail):
            decodificar_palavra("=?nao-existe?B?YQ==?=")


if __name__ == "__main__":
    unittest.main()
