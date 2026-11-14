"""Reimplementação simplificada do comm (listas ordenadas, colunas 1/2/3)."""
import sys
from typing import Optional, TextIO


def comparar(a: list[str], b: list[str]) -> list[tuple[int, str]]:
    """Retorna (coluna, linha): 1 só em a, 2 só em b, 3 em ambos. Entradas ordenadas."""
    i = j = 0
    res: list[tuple[int, str]] = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            res.append((3, a[i]))
            i += 1
            j += 1
        elif a[i] < b[j]:
            res.append((1, a[i]))
            i += 1
        else:
            res.append((2, b[j]))
            j += 1
    res.extend((1, x) for x in a[i:])
    res.extend((2, x) for x in b[j:])
    return res


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    suprimir = set()
    arquivos = []
    for a in argv:
        if a.startswith("-") and len(a) > 1:
            if any(ch not in "123" for ch in a[1:]):
                print(f"comm: opção inválida -- '{a}'", file=sys.stderr)
                return 2
            suprimir.update(int(ch) for ch in a[1:])
        else:
            arquivos.append(a)
    if len(arquivos) != 2:
        print("uso: comm [-123] arquivo1 arquivo2", file=sys.stderr)
        return 2
    conteudo = []
    for nome in arquivos:
        try:
            with open(nome, encoding="utf-8") as f:
                conteudo.append(f.read().splitlines())
        except OSError as e:
            print(f"comm: {nome}: {e.strerror}", file=sys.stderr)
            return 1
    for col, linha in comparar(*conteudo):
        if col in suprimir:
            continue
        recuo = sum(1 for c in (1, 2, 3) if c < col and c not in suprimir)
        print("\t" * recuo + linha, file=saida)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
