// Todas as funções trabalham em UTC para resultados determinísticos.
const DIA = 86400000;

export const ehBissexto = (ano) => (ano % 4 === 0 && ano % 100 !== 0) || ano % 400 === 0;

export function diasNoMes(ano, mes) {
  return [31, ehBissexto(ano) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mes - 1];
}

export function addDias(data, n) {
  return new Date(new Date(data).getTime() + n * DIA);
}

// Diferença em dias inteiros entre duas datas (b - a), truncando.
export function diffDias(a, b) {
  return Math.trunc((new Date(b) - new Date(a)) / DIA);
}

// Início da semana (00:00 UTC). inicio: 0 = domingo, 1 = segunda.
export function inicioDaSemana(data, inicio = 0) {
  const d = new Date(data);
  const base = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate());
  const delta = (d.getUTCDay() - inicio + 7) % 7;
  return new Date(base - delta * DIA);
}

// Formata como AAAA-MM-DD.
export const formatarISO = (data) => new Date(data).toISOString().slice(0, 10);
