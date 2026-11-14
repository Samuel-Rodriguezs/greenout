import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "validacao.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestValidacao(unittest.TestCase):
    def ok(self, tipo, valor):
        r = executar(tipo, valor)
        self.assertEqual((r.returncode, r.stdout), (0, "valido\n"), (tipo, valor))

    def ruim(self, tipo, valor):
        r = executar(tipo, valor)
        self.assertEqual((r.returncode, r.stdout), (1, "invalido\n"), (tipo, valor))

    def test_inteiro(self):
        for v in ("0", "42", "-7", "+3"):
            self.ok("inteiro", v)
        for v in ("", "1.5", "abc", "1a"):
            self.ruim("inteiro", v)

    def test_email(self):
        for v in ("a@b.com", "nome.sobrenome+tag@sub.dominio.com.br"):
            self.ok("email", v)
        for v in ("a@b", "@b.com", "a b@c.com", "a@.com", "semarroba"):
            self.ruim("email", v)

    def test_ip(self):
        for v in ("0.0.0.0", "192.168.1.1", "255.255.255.255"):
            self.ok("ip", v)
        for v in ("256.1.1.1", "1.2.3", "1.2.3.4.5", "01.2.3.4", "a.b.c.d"):
            self.ruim("ip", v)

    def test_cpf(self):
        self.ok("cpf", "529.982.247-25")
        self.ok("cpf", "52998224725")
        self.ruim("cpf", "529.982.247-26")
        self.ruim("cpf", "111.111.111-11")
        self.ruim("cpf", "123")

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; val_ip 10.0.0.1 && echo sim'],
                           capture_output=True, text=True)
        self.assertEqual(r.stdout, "sim\n")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("cnpj", "1").returncode, 2)
        self.assertEqual(executar("cpf").returncode, 2)


if __name__ == "__main__":
    unittest.main()
