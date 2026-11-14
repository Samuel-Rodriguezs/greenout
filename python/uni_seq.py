"""Reimplementação do seq (inteiros): seq FIM | seq INI FIM | seq INI PASSO FIM."""
import sys
from typing import Optional, TextIO


def sequencia(ini: int, passo: int, fim: int) -> list[int]:
    if passo == 0:
        raise ValueError("o passo não pode ser zero")
    if passo > 0:
        return list(range(ini, fim + 1, passo))
    return list(range(ini, fim - 1, passo))


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    try:
        nums = [int(a) for a in argv]
    except ValueError:
        print("seq: argumento numérico inválido", file=sys.stderr)
        return 2
    if len(nums) == 1:
        ini, passo, fim = 1, 1, nums[0]
    elif len(nums) == 2:
        ini, passo, fim = nums[0], 1, nums[1]
    elif len(nums) == 3:
        ini, passo, fim = nums
    else:
        print("uso: seq [INI [PASSO]] FIM", file=sys.stderr)
        return 2
    try:
        valores = sequencia(ini, passo, fim)
    except ValueError as e:
        print(f"seq: {e}", file=sys.stderr)
        return 2
    for v in valores:
        print(v, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
