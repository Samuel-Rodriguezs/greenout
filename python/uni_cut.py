"""Reimplementação simplificada do cut (-d delimitador -f campos)."""
import sys
from typing import Optional, TextIO


def parse_campos(spec: str) -> list[int]:
    """Converte '1,3-4' em [1, 3, 4] (índices começando em 1)."""
    campos: list[int] = []
    for parte in spec.split(","):
        if not parte:
            raise ValueError("lista de campos inválida")
        try:
            if "-" in parte:
                ini, fim = parte.split("-", 1)
                a, b = int(ini), int(fim)
                if a < 1 or b < a:
                    raise ValueError
                campos.extend(range(a, b + 1))
            else:
                n = int(parte)
                if n < 1:
                    raise ValueError
                campos.append(n)
        except ValueError:
            raise ValueError(f"campo inválido '{parte}'") from None
    return sorted(set(campos))


def cortar(linhas: list[str], campos: list[int], delim: str = "\t") -> list[str]:
    saida = []
    for l in linhas:
        if delim not in l:
            saida.append(l)  # como o cut: linha sem delimitador passa intacta
            continue
        partes = l.split(delim)
        saida.append(delim.join(partes[c - 1] for c in campos if c <= len(partes)))
    return saida


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    delim, spec = "\t", None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-d", "-f") and i + 1 < len(argv):
            if a == "-d":
                delim = argv[i + 1]
            else:
                spec = argv[i + 1]
            i += 2
        else:
            print(f"cut: argumento inválido '{a}'", file=sys.stderr)
            return 2
    if spec is None:
        print("cut: é necessário especificar -f", file=sys.stderr)
        return 2
    if len(delim) != 1:
        print("cut: o delimitador deve ser um único caractere", file=sys.stderr)
        return 2
    try:
        campos = parse_campos(spec)
    except ValueError as e:
        print(f"cut: {e}", file=sys.stderr)
        return 2
    for l in cortar(entrada.splitlines(), campos, delim):
        print(l, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
