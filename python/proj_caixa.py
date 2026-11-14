"""Simulador de caixa eletronico com PIN, limite diario e cedulas."""
from typing import Dict, List

CEDULAS = (100, 50, 20, 10)


class ErroCaixa(Exception):
    pass


class CaixaEletronico:
    def __init__(self, pin: str, saldo: int, limite_diario: int = 1000) -> None:
        self._pin = pin
        self.saldo = saldo
        self.limite_diario = limite_diario
        self.sacado_hoje = 0
        self.autenticado = False
        self.tentativas = 0
        self.bloqueado = False
        self.extrato: List[str] = []

    def autenticar(self, pin: str) -> bool:
        if self.bloqueado:
            raise ErroCaixa("cartao bloqueado")
        if pin == self._pin:
            self.autenticado = True
            self.tentativas = 0
            return True
        self.tentativas += 1
        if self.tentativas >= 3:
            self.bloqueado = True
        return False

    def _exigir_login(self) -> None:
        if not self.autenticado:
            raise ErroCaixa("nao autenticado")

    def depositar(self, valor: int) -> None:
        self._exigir_login()
        if valor <= 0:
            raise ErroCaixa("valor invalido")
        self.saldo += valor
        self.extrato.append(f"deposito {valor}")

    def sacar(self, valor: int) -> Dict[int, int]:
        self._exigir_login()
        if valor <= 0 or valor % 10:
            raise ErroCaixa("valor invalido")
        if valor > self.saldo:
            raise ErroCaixa("saldo insuficiente")
        if self.sacado_hoje + valor > self.limite_diario:
            raise ErroCaixa("limite diario excedido")
        notas: Dict[int, int] = {}
        resto = valor
        for c in CEDULAS:
            if resto >= c:
                notas[c], resto = divmod(resto, c)
        self.saldo -= valor
        self.sacado_hoje += valor
        self.extrato.append(f"saque {valor}")
        return notas

    def sair(self) -> None:
        self.autenticado = False
