import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "python"))

from fizzbuzz import fizzbuzz


class TestFizzBuzz(unittest.TestCase):
    def test_primeiros_quinze(self):
        esperado = ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
                    "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]
        self.assertEqual(fizzbuzz(15), esperado)

    def test_zero(self):
        self.assertEqual(fizzbuzz(0), [])


if __name__ == "__main__":
    unittest.main()
