const LOCALE = 'pt-BR';

export const formatarNumero = (n, { casas = 0, minCasas } = {}) =>
  new Intl.NumberFormat(LOCALE, { maximumFractionDigits: casas, minimumFractionDigits: minCasas ?? 0 }).format(n);

export const formatarMoeda = (n, moeda = 'BRL') =>
  new Intl.NumberFormat(LOCALE, { style: 'currency', currency: moeda }).format(n);

export const formatarPercentual = (fracao, casas = 0) =>
  new Intl.NumberFormat(LOCALE, { style: 'percent', maximumFractionDigits: casas, minimumFractionDigits: casas }).format(fracao);

export const formatarCompacto = (n) =>
  new Intl.NumberFormat(LOCALE, { notation: 'compact', maximumFractionDigits: 1 }).format(n);

const TZ = 'America/Sao_Paulo';

export const formatarData = (d, estilo = 'curta') => {
  const opts = {
    curta: { day: '2-digit', month: '2-digit', year: 'numeric' },
    longa: { day: 'numeric', month: 'long', year: 'numeric' },
    hora: { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false },
  }[estilo];
  if (!opts) throw new Error(`Estilo desconhecido: ${estilo}`);
  return new Intl.DateTimeFormat(LOCALE, { ...opts, timeZone: TZ }).format(new Date(d));
};

export function tempoRelativo(data, agora = Date.now()) {
  const diff = (new Date(data).getTime() - new Date(agora).getTime()) / 1000;
  const rtf = new Intl.RelativeTimeFormat(LOCALE, { numeric: 'auto' });
  const unidades = [
    ['year', 31536000], ['month', 2592000], ['day', 86400], ['hour', 3600], ['minute', 60],
  ];
  for (const [u, s] of unidades) {
    if (Math.abs(diff) >= s) return rtf.format(Math.trunc(diff / s), u);
  }
  return rtf.format(Math.trunc(diff), 'second');
}

export const formatarLista = (itens) =>
  new Intl.ListFormat(LOCALE, { style: 'long', type: 'conjunction' }).format(itens);

// Aceita "1.234,56", "R$ 1.234,56", "-12,5" e devolve número (NaN se inválido)
export function parseNumeroBR(texto) {
  const s = String(texto).replace(/[^\d,.-]/g, '');
  if (!/\d/.test(s)) return NaN;
  return Number(s.replace(/\./g, '').replace(',', '.'));
}
