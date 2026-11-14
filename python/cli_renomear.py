"""Renomeador em lote de arquivos com suporte a --dry-run."""
import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


def planejar(pasta: Path, padrao: str, substituto: str, regex: bool = False) -> List[Tuple[Path, Path]]:
    plano: List[Tuple[Path, Path]] = []
    for arq in sorted(pasta.iterdir()):
        if not arq.is_file():
            continue
        novo = re.sub(padrao, substituto, arq.name) if regex else arq.name.replace(padrao, substituto)
        if novo != arq.name:
            plano.append((arq, arq.with_name(novo)))
    destinos = [d for _, d in plano]
    if len(set(destinos)) != len(destinos) or any(d.exists() for d in destinos):
        raise ValueError("conflito: nomes de destino duplicados ou já existentes")
    return plano


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Renomeia arquivos de uma pasta em lote.")
    p.add_argument("pasta")
    p.add_argument("padrao")
    p.add_argument("substituto")
    p.add_argument("--regex", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="só mostra o que seria feito")
    a = p.parse_args(argv)
    pasta = Path(a.pasta)
    if not pasta.is_dir():
        print("erro: pasta inválida", file=sys.stderr)
        return 1
    try:
        plano = planejar(pasta, a.padrao, a.substituto, a.regex)
    except (ValueError, re.error) as e:
        print(f"erro: {e}", file=sys.stderr)
        return 1
    for origem, destino in plano:
        print(f"{origem.name} -> {destino.name}")
        if not a.dry_run:
            origem.rename(destino)
    print(f"{len(plano)} arquivo(s) {'a renomear' if a.dry_run else 'renomeado(s)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
