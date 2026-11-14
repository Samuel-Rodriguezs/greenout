import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from dp_bridge import AvisoCobranca, AvisoEntrega, CanalEmail, CanalSms


class TestBridge(unittest.TestCase):
    def test_combinacoes(self):
        email, sms = CanalEmail(), CanalSms()
        AvisoCobranca(email).notificar("a@x.com", "R$ 10")
        AvisoEntrega(sms).notificar("1199", "42")
        self.assertIn("Cobranca pendente: R$ 10", email.caixa[0][1])
        self.assertTrue(email.caixa[0][1].startswith("Assunto"))
        self.assertEqual(sms.caixa[0], ("1199", "Pedido 42 saiu para entrega"))

    def test_sms_trunca(self):
        sms = CanalSms()
        AvisoCobranca(sms).notificar("1", "x" * 100)
        self.assertEqual(len(sms.caixa[0][1]), 40)

    def test_trocar_canal(self):
        n = AvisoEntrega(CanalEmail())
        novo = CanalSms()
        n.canal = novo
        n.notificar("1", "7")
        self.assertEqual(len(novo.caixa), 1)


if __name__ == "__main__":
    unittest.main()
