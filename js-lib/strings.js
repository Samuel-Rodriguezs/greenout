const palavras = (s) =>
  String(s)
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .split(/[^A-Za-z0-9]+/)
    .filter(Boolean);

export const capitalize = (s) => (s ? s[0].toUpperCase() + s.slice(1).toLowerCase() : '');

export function camelCase(s) {
  return palavras(s).map((p, i) => (i === 0 ? p.toLowerCase() : capitalize(p))).join('');
}
export const kebabCase = (s) => palavras(s).map((p) => p.toLowerCase()).join('-');
export const snakeCase = (s) => palavras(s).map((p) => p.toLowerCase()).join('_');
// Gera slug de URL (sem acentos, minúsculo, separado por hífen).
export const slugify = kebabCase;
