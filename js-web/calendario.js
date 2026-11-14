// Grade de calendário (semanas começam no domingo por padrão). mes: 1-12.
const pad = (n) => String(n).padStart(2, '0');
const iso = (y, m, d) => `${y}-${pad(m)}-${pad(d)}`;

export const diasNoMes = (ano, mes) => new Date(Date.UTC(ano, mes, 0)).getUTCDate();
export const bissexto = (ano) => (ano % 4 === 0 && ano % 100 !== 0) || ano % 400 === 0;
export const diaDaSemana = (ano, mes, dia) => new Date(Date.UTC(ano, mes - 1, dia)).getUTCDay();

export function gradeDoMes(ano, mes, { inicioSemana = 0, hoje = null, feriados = [] } = {}) {
  if (mes < 1 || mes > 12) throw new RangeError('mes deve estar entre 1 e 12');
  const total = diasNoMes(ano, mes);
  const offset = (diaDaSemana(ano, mes, 1) - inicioSemana + 7) % 7;
  const feriadoSet = new Set(feriados);
  const celulas = [];
  for (let i = -offset; celulas.length % 7 !== 0 || i <= total - 1 + 0; i++) {
    const dt = new Date(Date.UTC(ano, mes - 1, 1 + i));
    const y = dt.getUTCFullYear();
    const m = dt.getUTCMonth() + 1;
    const d = dt.getUTCDate();
    const data = iso(y, m, d);
    celulas.push({
      data,
      dia: d,
      doMes: m === mes && y === ano,
      hoje: data === hoje,
      fimDeSemana: [0, 6].includes(dt.getUTCDay()),
      feriado: feriadoSet.has(data),
    });
    if (i > total - 1 && celulas.length % 7 === 0) break;
  }
  const semanas = [];
  for (let i = 0; i < celulas.length; i += 7) semanas.push(celulas.slice(i, i + 7));
  return semanas;
}

export function mesAnterior(ano, mes) {
  return mes === 1 ? { ano: ano - 1, mes: 12 } : { ano, mes: mes - 1 };
}
export function mesSeguinte(ano, mes) {
  return mes === 12 ? { ano: ano + 1, mes: 1 } : { ano, mes: mes + 1 };
}

export function nomeDoMes(mes, locale = 'pt-BR') {
  return new Intl.DateTimeFormat(locale, { month: 'long', timeZone: 'UTC' }).format(new Date(Date.UTC(2024, mes - 1, 1)));
}

export function cabecalhoSemana(inicioSemana = 0, locale = 'pt-BR') {
  const fmt = new Intl.DateTimeFormat(locale, { weekday: 'short', timeZone: 'UTC' });
  // 2023-01-01 é domingo
  return Array.from({ length: 7 }, (_, i) => fmt.format(new Date(Date.UTC(2023, 0, 1 + ((inicioSemana + i) % 7)))));
}

export function diasUteisEntre(inicioIso, fimIso) {
  let n = 0;
  const fim = Date.parse(fimIso);
  for (let t = Date.parse(inicioIso); t <= fim; t += 86400000) {
    const w = new Date(t).getUTCDay();
    if (w !== 0 && w !== 6) n++;
  }
  return n;
}
