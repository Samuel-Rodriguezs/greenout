// Formatação e leitura de moeda em pt-BR usando Intl.

const formatador = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

/** Formata um número como "R$ 1.234,56". Espaço não separável é normalizado para espaço comum. */
export function formatarMoeda(valor) {
  if (typeof valor !== 'number' || !Number.isFinite(valor)) {
    throw new TypeError('valor deve ser um número finito');
  }
  // Evita "-R$ 0,00" para valores que arredondam para zero.
  const arredondado = Math.round(valor * 100) / 100;
  return formatador.format(arredondado === 0 ? 0 : arredondado).replace(/ /g, ' ');
}

/** Converte "R$ 1.234,56" (ou "1234,56", "-R$ 5,00") em número. Retorna NaN se inválido. */
export function lerMoeda(texto) {
  if (typeof texto !== 'string') return NaN;
  const limpo = texto.replace(/[R$\s ]/g, '');
  if (!/^-?(\d{1,3}(\.\d{3})*|\d+)(,\d+)?$/.test(limpo)) return NaN;
  return Number(limpo.replace(/\./g, '').replace(',', '.'));
}
