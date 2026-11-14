"""Reimplementação simplificada do grep (-i -v -n -c)."""
import re
import sys
from typing import Optional, TextIO


def filtrar(linhas: list[str], padrao: str, ignorar_caixa: bool = False,
            inverter: bool = False) -> list[tuple[int, str]]:
    """Retorna pares (número da linha começando em 1, linha) que casam."""
    regex = re.compile(padrao, re.IGNORECASE if ignorar_caixa else 0)
    return [(i, l) for i, l in enumerate(linhas, 1)
            if bool(regex.search(l)) != inverter]


def main(argv: list[str], entrada: str = "", saida: Optional[TextIO] = None) -> int:
    saida = saida or sys.stdout
    flags = set()
    posicionais = []
    for a in argv:
        if a.startswith("-") and len(a) > 1:
            if any(ch not in "ivnc" for ch in a[1:]):
                print(f"grep: opção inválida -- '{a}'", file=sys.stderr)
                return 2
            flags.update(a[1:])
        else:
            posicionais.append(a)
    if not posicionais:
        print("uso: grep [-ivnc] padrao [arquivo...]", file=sys.stderr)
        return 2
    try:
        _ = re.compile(posicionais[0])
    except re.error as e:
        print(f"grep: regex inválida: {e}", file=sys.stderr)
        return 2
    padrao, arquivos = posicionais[0], posicionais[1:]
    fontes = []
    status_erro = False
    if arquivos:
        for nome in arquivos:
            try:
                with open(nome, encoding="utf-8") as f:
                    fontes.append((nome, f.read()))
            except OSError as e:
                print(f"grep: {nome}: {e.strerror}", file=sys.stderr)
                status_erro = True
    else:
        fontes.append((None, entrada))
    achou = False
    for nome, texto in fontes:
        res = filtrar(texto.splitlines(), padrao, "i" in flags, "v" in flags)
        achou = achou or bool(res)
        prefixo = f"{nome}:" if nome and len(arquivos) > 1 else ""
        if "c" in flags:
            print(f"{prefixo}{len(res)}", file=saida)
            continue
        for i, l in res:
            num = f"{i}:" if "n" in flags else ""
            print(f"{prefixo}{num}{l}", file=saida)
    if status_erro:
        return 2
    return 0 if achou else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], "" if sys.stdin.isatty() else sys.stdin.read()))
