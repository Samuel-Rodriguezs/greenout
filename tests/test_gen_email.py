import random
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_email as g


class TestGenEmail(unittest.TestCase):
    def test_remover_acentos(self):
        self.assertEqual(g.remover_acentos("João Araújo"), "Joao Araujo")

    def test_formato_e_derivacao(self):
        rng = random.Random(1)
        for _ in range(50):
            e = g.email_do_nome("André de Souza Lima", rng)
            self.assertRegex(e, r"^[a-z0-9._]+@[a-z.]+$")
            self.assertTrue(e.startswith(("andre", "a")))
            self.assertIn(e.split("@")[1], g.DOMINIOS)

    def test_dominio_fixo(self):
        e = g.email_do_nome("Maria Silva", random.Random(2), "x.example")
        self.assertTrue(e.endswith("@x.example"))

    def test_nome_vazio(self):
        with self.assertRaises(ValueError):
            g.email_do_nome("de da", random.Random(0))

    def test_determinismo_e_unicidade(self):
        a = g.gerar_emails_unicos(random.Random(9), 300)
        b = g.gerar_emails_unicos(random.Random(9), 300)
        self.assertEqual(a, b)
        emails = [e for _, e in a]
        self.assertEqual(len(set(emails)), 300)
        self.assertTrue(all(re.match(r"^[^@\s]+@[^@\s]+$", e) for e in emails))


if __name__ == "__main__":
    unittest.main()
