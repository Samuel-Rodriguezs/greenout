// Corta o texto em `max` caracteres (incluindo o sufixo).
export function truncate(texto, max, sufixo = '…') {
  if (texto.length <= max) return texto;
  if (max <= sufixo.length) return sufixo.slice(0, Math.max(0, max));
  return texto.slice(0, max - sufixo.length) + sufixo;
}
// Corta em limite de palavra quando possível.
export function truncatePalavras(texto, max, sufixo = '…') {
  if (texto.length <= max) return texto;
  const corte = texto.slice(0, Math.max(0, max - sufixo.length));
  const i = corte.lastIndexOf(' ');
  return (i > 0 ? corte.slice(0, i) : corte).trimEnd() + sufixo;
}
// Preenche à esquerda com zeros (ou outro caractere) até `tam`.
export const padEsquerda = (v, tam, c = '0') => String(v).padStart(tam, c);
export const padDireita = (v, tam, c = ' ') => String(v).padEnd(tam, c);
// Centraliza o texto numa largura.
export function padCentro(v, tam, c = ' ') {
  const s = String(v);
  const falta = Math.max(0, tam - s.length);
  const esq = Math.floor(falta / 2);
  return c.repeat(esq) + s + c.repeat(falta - esq);
}
