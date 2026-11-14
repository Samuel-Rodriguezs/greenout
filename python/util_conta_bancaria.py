class SaldoInsuficienteError(Exception):
    """Saque ou transferência maior que o saldo disponível."""


class ValorInvalidoError(ValueError):
    """Valor não positivo ou não numérico."""


class ContaBancaria:
    def __init__(self, titular: str, saldo_inicial: float = 0.0) -> None:
        if not titular or not titular.strip():
            raise ValueError("titular é obrigatório")
        if saldo_inicial < 0:
            raise ValorInvalidoError("saldo inicial não pode ser negativo")
        self.titular = titular.strip()
        self._saldo = float(saldo_inicial)
        self._extrato: list[tuple[str, float]] = []

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def extrato(self) -> list[tuple[str, float]]:
        return list(self._extrato)

    @staticmethod
    def _validar(valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValorInvalidoError("valor deve ser numérico")
        if valor <= 0:
            raise ValorInvalidoError("valor deve ser positivo")

    def depositar(self, valor: float) -> float:
        self._validar(valor)
        self._saldo += valor
        self._extrato.append(("deposito", float(valor)))
        return self._saldo

    def sacar(self, valor: float) -> float:
        self._validar(valor)
        if valor > self._saldo:
            raise SaldoInsuficienteError(
                f"saldo {self._saldo:.2f} insuficiente para sacar {valor:.2f}"
            )
        self._saldo -= valor
        self._extrato.append(("saque", float(valor)))
        return self._saldo

    def transferir(self, destino: "ContaBancaria", valor: float) -> None:
        if destino is self:
            raise ValueError("não é possível transferir para a mesma conta")
        self.sacar(valor)
        destino.depositar(valor)
