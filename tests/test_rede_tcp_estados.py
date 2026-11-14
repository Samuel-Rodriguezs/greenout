import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from rede_tcp_estados import (ABRIR_ATIVO, ABRIR_PASSIVO, FECHAR, RCV_ACK, RCV_FIN,
                              RCV_FIN_ACK, RCV_RST, RCV_SYN, RCV_SYN_ACK,
                              TIMEOUT_2MSL, ConexaoTCP, Estado, TransicaoInvalida)

E = Estado


class TestRedeTcpEstados(unittest.TestCase):
    def test_handshake_cliente_servidor(self):
        cli, srv = ConexaoTCP(), ConexaoTCP()
        self.assertIsNone(srv.processar(ABRIR_PASSIVO))
        self.assertEqual(cli.processar(ABRIR_ATIVO), "SYN")
        self.assertEqual(srv.processar(RCV_SYN), "SYN+ACK")
        self.assertEqual(cli.processar(RCV_SYN_ACK), "ACK")
        self.assertIsNone(srv.processar(RCV_ACK))
        self.assertEqual((cli.estado, srv.estado), (E.ESTABLISHED, E.ESTABLISHED))
        self.assertTrue(cli.sincronizada)

    def test_encerramento_ativo_normal(self):
        c = ConexaoTCP()
        c.processar(ABRIR_ATIVO)
        c.processar(RCV_SYN_ACK)
        self.assertEqual(c.processar(FECHAR), "FIN")
        self.assertEqual(c.estado, E.FIN_WAIT_1)
        c.processar(RCV_ACK)
        self.assertEqual(c.estado, E.FIN_WAIT_2)
        self.assertEqual(c.processar(RCV_FIN), "ACK")
        self.assertEqual(c.estado, E.TIME_WAIT)
        c.processar(TIMEOUT_2MSL)
        self.assertEqual(c.estado, E.CLOSED)
        self.assertEqual(c.historico, [E.CLOSED, E.SYN_SENT, E.ESTABLISHED, E.FIN_WAIT_1,
                                       E.FIN_WAIT_2, E.TIME_WAIT, E.CLOSED])

    def test_encerramento_passivo(self):
        c = ConexaoTCP()
        c.processar(ABRIR_PASSIVO)
        c.processar(RCV_SYN)
        c.processar(RCV_ACK)
        self.assertEqual(c.processar(RCV_FIN), "ACK")
        self.assertEqual(c.estado, E.CLOSE_WAIT)
        self.assertEqual(c.processar(FECHAR), "FIN")
        self.assertEqual(c.estado, E.LAST_ACK)
        c.processar(RCV_ACK)
        self.assertEqual(c.estado, E.CLOSED)

    def test_encerramento_simultaneo(self):
        c = ConexaoTCP()
        c.processar(ABRIR_ATIVO)
        c.processar(RCV_SYN_ACK)
        c.processar(FECHAR)
        self.assertEqual(c.processar(RCV_FIN), "ACK")
        self.assertEqual(c.estado, E.CLOSING)
        c.processar(RCV_ACK)
        self.assertEqual(c.estado, E.TIME_WAIT)

    def test_fin_ack_combinado(self):
        c = ConexaoTCP()
        c.processar(ABRIR_ATIVO)
        c.processar(RCV_SYN_ACK)
        c.processar(FECHAR)
        c.processar(RCV_FIN_ACK)
        self.assertEqual(c.estado, E.TIME_WAIT)

    def test_abertura_simultanea(self):
        c = ConexaoTCP()
        c.processar(ABRIR_ATIVO)
        self.assertEqual(c.processar(RCV_SYN), "SYN+ACK")
        self.assertEqual(c.estado, E.SYN_RCVD)
        c.processar(RCV_ACK)
        self.assertEqual(c.estado, E.ESTABLISHED)

    def test_rst(self):
        c = ConexaoTCP()
        c.processar(ABRIR_ATIVO)
        c.processar(RCV_SYN_ACK)
        c.processar(RCV_RST)
        self.assertEqual(c.estado, E.CLOSED)
        srv = ConexaoTCP()
        srv.processar(ABRIR_PASSIVO)
        srv.processar(RCV_RST)
        self.assertEqual(srv.estado, E.LISTEN)

    def test_invalido(self):
        c = ConexaoTCP()
        with self.assertRaises(TransicaoInvalida):
            c.processar(RCV_ACK)
        self.assertEqual(c.estado, E.CLOSED)
        c.processar(ABRIR_ATIVO)
        c.processar(RCV_SYN_ACK)
        with self.assertRaises(TransicaoInvalida):
            c.processar(ABRIR_ATIVO)
        with self.assertRaises(TransicaoInvalida):
            c.processar(TIMEOUT_2MSL)

    def test_fechar_antes_de_conectar(self):
        c = ConexaoTCP()
        c.processar(ABRIR_PASSIVO)
        c.processar(FECHAR)
        self.assertEqual(c.estado, E.CLOSED)


if __name__ == "__main__":
    unittest.main()
