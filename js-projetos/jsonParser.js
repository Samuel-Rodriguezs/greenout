// Parser de JSON próprio (descida recursiva), compatível com a RFC 8259.
// Erros informam a posição do problema.

const ESCAPES = { '"': '"', '\\': '\\', '/': '/', b: '\b', f: '\f', n: '\n', r: '\r', t: '\t' };

export class ErroJson extends SyntaxError {
  constructor(mensagem, posicao) {
    super(`${mensagem} na posição ${posicao}`);
    this.posicao = posicao;
  }
}

export function parseJson(texto) {
  let i = 0;
  const falhar = (msg) => { throw new ErroJson(msg, i); };
  const espaco = () => { while (' \t\n\r'.includes(texto[i]) && i < texto.length) i++; };

  function valor() {
    espaco();
    const c = texto[i];
    if (c === undefined) falhar('Fim inesperado');
    if (c === '{') return objeto();
    if (c === '[') return lista();
    if (c === '"') return string();
    if (c === '-' || (c >= '0' && c <= '9')) return numero();
    for (const [lit, v] of [['true', true], ['false', false], ['null', null]]) {
      if (texto.startsWith(lit, i)) { i += lit.length; return v; }
    }
    return falhar(`Caractere inesperado '${c}'`);
  }

  function objeto() {
    const obj = {};
    i++;
    espaco();
    if (texto[i] === '}') { i++; return obj; }
    for (;;) {
      espaco();
      if (texto[i] !== '"') falhar('Chave deve ser string');
      const k = string();
      espaco();
      if (texto[i++] !== ':') { i--; falhar("Esperado ':'"); }
      Object.defineProperty(obj, k, { value: valor(), enumerable: true, writable: true, configurable: true });
      espaco();
      const c = texto[i++];
      if (c === '}') return obj;
      if (c !== ',') { i--; falhar("Esperado ',' ou '}'"); }
    }
  }

  function lista() {
    const arr = [];
    i++;
    espaco();
    if (texto[i] === ']') { i++; return arr; }
    for (;;) {
      arr.push(valor());
      espaco();
      const c = texto[i++];
      if (c === ']') return arr;
      if (c !== ',') { i--; falhar("Esperado ',' ou ']'"); }
    }
  }

  function string() {
    let s = '';
    i++;
    for (;;) {
      const c = texto[i++];
      if (c === undefined) { i--; falhar('String não terminada'); }
      if (c === '"') return s;
      if (c < ' ') { i--; falhar('Caractere de controle em string'); }
      if (c !== '\\') { s += c; continue; }
      const e = texto[i++];
      if (e === 'u') {
        const hex = texto.slice(i, i + 4);
        if (!/^[0-9a-fA-F]{4}$/.test(hex)) falhar('Escape unicode inválido');
        s += String.fromCharCode(parseInt(hex, 16));
        i += 4;
      } else if (e in ESCAPES) s += ESCAPES[e];
      else { i--; falhar('Escape inválido'); }
    }
  }

  function numero() {
    const m = /^-?(0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?/.exec(texto.slice(i));
    if (!m) falhar('Número inválido');
    i += m[0].length;
    return Number(m[0]);
  }

  const resultado = valor();
  espaco();
  if (i < texto.length) falhar('Conteúdo extra após o valor');
  return resultado;
}

export function stringifyJson(v, indent = 0, nivel = 0) {
  const quebra = indent ? `\n${' '.repeat(indent * (nivel + 1))}` : '';
  const fim = indent ? `\n${' '.repeat(indent * nivel)}` : '';
  if (v === null || typeof v === 'boolean') return String(v);
  if (typeof v === 'number') return Number.isFinite(v) ? String(v) : 'null';
  if (typeof v === 'string') return JSON.stringify(v);
  if (Array.isArray(v)) {
    if (!v.length) return '[]';
    return `[${quebra}${v.map((x) => stringifyJson(x, indent, nivel + 1)).join(`,${quebra}`)}${fim}]`;
  }
  const chaves = Object.keys(v).filter((k) => v[k] !== undefined);
  if (!chaves.length) return '{}';
  const sep = indent ? ': ' : ':';
  return `{${quebra}${chaves.map((k) => JSON.stringify(k) + sep + stringifyJson(v[k], indent, nivel + 1)).join(`,${quebra}`)}${fim}}`;
}
