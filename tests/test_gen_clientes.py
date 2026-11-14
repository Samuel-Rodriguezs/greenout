import json
import random
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

import gen_clientes as g
from dt_cep import validar_cep
from gen_nascimento import idade_em
from gen_nomes import NOMES_FEMININOS, NOMES_MASCULINOS
from gen_telefone import eh_celular_valido
from util_cpf import validar_cpf

REF = date(2025, 1, 15)


class TestGenClientes(unittest.TestCase):
    def test_determinismo(self):
        self.assertEqual(g.gerar_clientes(10, 40, REF), g.gerar_clientes(10, 40, REF))
        self.assertNotEqual(g.gerar_clientes(10, 40, REF), g.gerar_clientes(11, 40, REF))

    def test_campos_validos(self):
        for c in g.gerar_clientes(1, 300, REF):
            self.assertTrue(validar_cpf(c.cpf))
            self.assertTrue(eh_celular_valido(c.telefone))
            self.assertTrue(validar_cep(c.endereco.cep))
            self.assertTrue(18 <= idade_em(c.nascimento, REF) <= 85)
            primeiro = c.nome.split()[0]
            esperado = NOMES_MASCULINOS if c.genero == "M" else NOMES_FEMININOS
            self.assertIn(primeiro, esperado)
            self.assertIn("@", c.email)

    def test_unicidade_e_ids(self):
        cs = g.gerar_clientes(2, 500, REF)
        self.assertEqual([c.id for c in cs], list(range(1, 501)))
        self.assertEqual(len({c.cpf for c in cs}), 500)
        self.assertEqual(len({c.email for c in cs}), 500)

    def test_imutavel(self):
        c = g.gerar_cliente(random.Random(0), 1, REF)
        with self.assertRaises(Exception):
            c.nome = "outro"  # type: ignore[misc]

    def test_como_dict_serializavel(self):
        c = g.gerar_cliente(random.Random(3), 7, REF)
        d = c.como_dict()
        self.assertEqual(d["nascimento"], c.nascimento.isoformat())
        self.assertEqual(d["endereco"]["uf"], c.endereco.uf)
        self.assertEqual(json.loads(json.dumps(d))["id"], 7)

    def test_lote_vazio(self):
        self.assertEqual(g.gerar_clientes(1, 0, REF), [])


if __name__ == "__main__":
    unittest.main()
