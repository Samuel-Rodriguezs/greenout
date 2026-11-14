import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from cli_lorem import main


def rodar(args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = main(args)
    return code, buf.getvalue().strip()


class TestCliLorem(unittest.TestCase):
    def test_paragrafos(self):
        code, out = rodar(["-p", "4", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.split("\n\n")), 4)
        self.assertTrue(out.startswith("Lorem ipsum dolor sit amet."))

    def test_seed_reprodutivel(self):
        self.assertEqual(rodar(["--seed", "9"]), rodar(["--seed", "9"]))
        self.assertNotEqual(rodar(["--seed", "9"]), rodar(["--seed", "10"]))

    def test_limite_palavras(self):
        _, out = rodar(["--seed", "2", "--palavras", "5"])
        self.assertEqual(len(out.split()), 5)

    def test_invalido(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(["-p", "0"]), 1)


if __name__ == "__main__":
    unittest.main()
