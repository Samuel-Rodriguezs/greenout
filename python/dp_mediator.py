"""Mediator: sala de chat que intermedia mensagens entre usuários."""
from __future__ import annotations


class SalaChat:
    def __init__(self) -> None:
        self._usuarios: dict[str, "Usuario"] = {}

    def entrar(self, usuario: "Usuario") -> None:
        if usuario.nome in self._usuarios:
            raise ValueError(f"nome em uso: {usuario.nome}")
        self._usuarios[usuario.nome] = usuario
        usuario.sala = self
        self.transmitir("sistema", f"{usuario.nome} entrou")

    def sair(self, usuario: "Usuario") -> None:
        if self._usuarios.pop(usuario.nome, None) is not None:
            usuario.sala = None
            self.transmitir("sistema", f"{usuario.nome} saiu")

    def transmitir(self, origem: str, texto: str) -> None:
        for nome, u in self._usuarios.items():
            if nome != origem:
                u.receber(origem, texto)

    def privada(self, origem: str, destino: str, texto: str) -> None:
        if destino not in self._usuarios:
            raise KeyError(destino)
        self._usuarios[destino].receber(origem, texto)


class Usuario:
    def __init__(self, nome: str) -> None:
        self.nome = nome
        self.sala: SalaChat | None = None
        self.recebidas: list[tuple[str, str]] = []

    def receber(self, origem: str, texto: str) -> None:
        self.recebidas.append((origem, texto))

    def falar(self, texto: str) -> None:
        if self.sala is None:
            raise RuntimeError("usuário fora da sala")
        self.sala.transmitir(self.nome, texto)

    def sussurrar(self, destino: str, texto: str) -> None:
        if self.sala is None:
            raise RuntimeError("usuário fora da sala")
        self.sala.privada(self.nome, destino, texto)
