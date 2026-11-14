// Calculadora de financiamento: sistemas Price (parcela fixa) e SAC (amortização constante).
// Taxa em % ao mês; valores em reais, arredondados em centavos.

const arredondar = (v) => Math.round((v + Number.EPSILON) * 100) / 100;

function validar(principal, taxaMensal, meses) {
  if (!(principal > 0)) throw new RangeError('Valor financiado deve ser positivo');
  if (!(taxaMensal >= 0)) throw new RangeError('Taxa não pode ser negativa');
  if (!Number.isInteger(meses) || meses < 1) throw new RangeError('Prazo deve ser inteiro e positivo');
}

export function parcelaPrice(principal, taxaMensal, meses) {
  validar(principal, taxaMensal, meses);
  const i = taxaMensal / 100;
  if (i === 0) return arredondar(principal / meses);
  return arredondar((principal * i) / (1 - (1 + i) ** -meses));
}

export function tabelaPrice(principal, taxaMensal, meses) {
  const parcela = parcelaPrice(principal, taxaMensal, meses);
  const i = taxaMensal / 100;
  let saldo = principal;
  const linhas = [];
  for (let n = 1; n <= meses; n++) {
    const juros = arredondar(saldo * i);
    // Na última parcela, quita o saldo restante para absorver arredondamentos.
    const amortizacao = n === meses ? arredondar(saldo) : arredondar(parcela - juros);
    saldo = arredondar(saldo - amortizacao);
    linhas.push({ numero: n, parcela: arredondar(juros + amortizacao), juros, amortizacao, saldo });
  }
  return linhas;
}

export function tabelaSac(principal, taxaMensal, meses) {
  validar(principal, taxaMensal, meses);
  const i = taxaMensal / 100;
  const amortConstante = principal / meses;
  let saldo = principal;
  const linhas = [];
  for (let n = 1; n <= meses; n++) {
    const juros = arredondar(saldo * i);
    const amortizacao = n === meses ? arredondar(saldo) : arredondar(amortConstante);
    saldo = arredondar(saldo - amortizacao);
    linhas.push({ numero: n, parcela: arredondar(juros + amortizacao), juros, amortizacao, saldo });
  }
  return linhas;
}

export function resumo(tabela) {
  const totalPago = arredondar(tabela.reduce((s, l) => s + l.parcela, 0));
  const totalJuros = arredondar(tabela.reduce((s, l) => s + l.juros, 0));
  return { totalPago, totalJuros, primeiraParcela: tabela[0].parcela, ultimaParcela: tabela.at(-1).parcela };
}

// Quanto posso financiar dada uma parcela máxima (inverso do Price).
export function valorFinanciavel(parcela, taxaMensal, meses) {
  validar(parcela, taxaMensal, meses);
  const i = taxaMensal / 100;
  if (i === 0) return arredondar(parcela * meses);
  return arredondar((parcela * (1 - (1 + i) ** -meses)) / i);
}
