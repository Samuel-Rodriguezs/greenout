// Conta bancária com event sourcing: o estado é sempre derivado dos eventos.
// Valores em centavos (inteiros) para evitar erros de ponto flutuante.

export const TIPOS = Object.freeze({
  ABERTA: 'ContaAberta',
  DEPOSITO: 'DepositoRealizado',
  SAQUE: 'SaqueRealizado',
  ENCERRADA: 'ContaEncerrada',
});

export function aplicar(estado, evento) {
  switch (evento.tipo) {
    case TIPOS.ABERTA:
      return { titular: evento.titular, saldo: 0, aberta: true, limite: evento.limite ?? 0 };
    case TIPOS.DEPOSITO:
      return { ...estado, saldo: estado.saldo + evento.valor };
    case TIPOS.SAQUE:
      return { ...estado, saldo: estado.saldo - evento.valor };
    case TIPOS.ENCERRADA:
      return { ...estado, aberta: false };
    default:
      throw new Error(`Evento desconhecido: ${evento.tipo}`);
  }
}

export function reconstruir(eventos) {
  return eventos.reduce(aplicar, null);
}

export class Conta {
  #eventos = [];

  constructor(eventos = []) {
    this.#eventos = [...eventos];
  }

  get estado() {
    return reconstruir(this.#eventos);
  }

  get eventos() {
    return [...this.#eventos];
  }

  #registrar(evento) {
    this.#eventos.push(Object.freeze(evento));
  }

  #exigirAberta() {
    const e = this.estado;
    if (!e) throw new Error('Conta não foi aberta');
    if (!e.aberta) throw new Error('Conta encerrada');
    return e;
  }

  static #validarValor(v) {
    if (!Number.isInteger(v) || v <= 0) throw new RangeError('Valor deve ser inteiro positivo (centavos)');
  }

  abrir(titular, limite = 0) {
    if (this.estado) throw new Error('Conta já aberta');
    if (!titular) throw new Error('Titular obrigatório');
    this.#registrar({ tipo: TIPOS.ABERTA, titular, limite });
  }

  depositar(valor) {
    Conta.#validarValor(valor);
    this.#exigirAberta();
    this.#registrar({ tipo: TIPOS.DEPOSITO, valor });
  }

  sacar(valor) {
    Conta.#validarValor(valor);
    const e = this.#exigirAberta();
    if (e.saldo - valor < -e.limite) throw new Error('Saldo insuficiente');
    this.#registrar({ tipo: TIPOS.SAQUE, valor });
  }

  encerrar() {
    const e = this.#exigirAberta();
    if (e.saldo !== 0) throw new Error('Saldo deve ser zero para encerrar');
    this.#registrar({ tipo: TIPOS.ENCERRADA });
  }

  // Saldo em um ponto do passado: aplica apenas os n primeiros eventos.
  saldoApos(n) {
    return reconstruir(this.#eventos.slice(0, n))?.saldo ?? 0;
  }
}
