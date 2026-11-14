import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bash-lib" / "strings.sh"


def executar(*args, entrada=None, env=None):
    return subprocess.run(["bash", str(SCRIPT), *args], input=entrada,
                          capture_output=True, text=True, env=env)


class TestStrings(unittest.TestCase):
    def test_trim(self):
        r = executar("trim", "   ola mundo \t ")
        self.assertEqual((r.returncode, r.stdout), (0, "ola mundo\n"))

    def test_upper_lower_len(self):
        self.assertEqual(executar("upper", "abc").stdout, "ABC\n")
        self.assertEqual(executar("lower", "ABC").stdout, "abc\n")
        self.assertEqual(executar("len", "abcd").stdout, "4\n")

    def test_join_split(self):
        self.assertEqual(executar("join", ",", "a", "b", "c").stdout, "a,b,c\n")
        self.assertEqual(executar("split", ":", "x:y::z").stdout, "x\ny\n\nz\n")

    def test_repeat_pad(self):
        self.assertEqual(executar("repeat", "ab", "3").stdout, "ababab\n")
        self.assertEqual(executar("pad_left", "7", "3", "0").stdout, "007\n")
        self.assertEqual(executar("pad_right", "ab", "5", ".").stdout, "ab...\n")
        self.assertEqual(executar("pad_left", "abcdef", "3").stdout, "abcdef\n")

    def test_source(self):
        r = subprocess.run(["bash", "-c", f'source "{SCRIPT}"; str_join - 1 2 3; str_trim "  x "'],
                           capture_output=True, text=True)
        self.assertEqual(r.stdout, "1-2-3\nx\n")

    def test_help(self):
        r = executar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Uso:", r.stdout)

    def test_erros(self):
        self.assertEqual(executar().returncode, 2)
        self.assertEqual(executar("inexistente").returncode, 2)
        self.assertEqual(executar("repeat", "a", "x").returncode, 1)
        self.assertEqual(executar("split", "ab", "a").returncode, 1)


if __name__ == "__main__":
    unittest.main()
