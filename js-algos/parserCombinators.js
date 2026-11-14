// Mini-biblioteca de parser combinators.
// Um parser é uma função (entrada, pos) => { ok: true, valor, pos } | { ok: false, pos, esperado }.

const sucesso = (valor, pos) => ({ ok: true, valor, pos });
const falha = (pos, esperado) => ({ ok: false, pos, esperado });

// Parser de string literal.
export const literal = (s) => (e, p) =>
  e.startsWith(s, p) ? sucesso(s, p + s.length) : falha(p, JSON.stringify(s));

// Parser por expressão regular (ancorada na posição atual).
export const regex = (re, descricao = String(re)) => {
  const r = new RegExp(re.source, re.flags.replace(/[gy]/g, '') + 'y');
  return (e, p) => {
    r.lastIndex = p;
    const m = r.exec(e);
    return m ? sucesso(m[0], p + m[0].length) : falha(p, descricao);
  };
};

export const fim = (e, p) => (p === e.length ? sucesso(null, p) : falha(p, 'fim da entrada'));

// Transforma o valor.
export const mapear = (parser, f) => (e, p) => {
  const r = parser(e, p);
  return r.ok ? sucesso(f(r.valor), r.pos) : r;
};

// Sequência: todos em ordem, valor = array.
export const sequencia = (...parsers) => (e, p) => {
  const valores = [];
  for (const parser of parsers) {
    const r = parser(e, p);
    if (!r.ok) return r;
    valores.push(r.valor);
    p = r.pos;
  }
  return sucesso(valores, p);
};

// Alternativa: primeiro que casar; em falha total reporta a que foi mais longe.
export const ou = (...parsers) => (e, p) => {
  let pior = null;
  for (const parser of parsers) {
    const r = parser(e, p);
    if (r.ok) return r;
    if (!pior || r.pos > pior.pos) pior = r;
    else if (r.pos === pior.pos) pior = falha(r.pos, `${pior.esperado} ou ${r.esperado}`);
  }
  return pior ?? falha(p, 'alternativa');
};

export const muitos = (parser) => (e, p) => {
  const valores = [];
  for (;;) {
    const r = parser(e, p);
    if (!r.ok || r.pos === p) return sucesso(valores, p); // evita laço infinito
    valores.push(r.valor);
    p = r.pos;
  }
};

export const umOuMais = (parser) => (e, p) => {
  const r = muitos(parser)(e, p);
  return r.valor.length ? r : falha(p, 'ao menos um');
};

export const opcional = (parser, padrao = null) => (e, p) => {
  const r = parser(e, p);
  return r.ok ? r : sucesso(padrao, p);
};

// Lista separada por um separador (zero ou mais itens).
export const separadoPor = (item, sep) => (e, p) => {
  const primeiro = item(e, p);
  if (!primeiro.ok) return sucesso([], p);
  const valores = [primeiro.valor];
  p = primeiro.pos;
  for (;;) {
    const s = sep(e, p);
    if (!s.ok) break;
    const r = item(e, s.pos);
    if (!r.ok) return r; // separador sem item depois
    valores.push(r.valor);
    p = r.pos;
  }
  return sucesso(valores, p);
};

// Descarta espaços em branco antes do parser.
export const token = (parser) => mapear(sequencia(regex(/\s*/), parser), ([, v]) => v);

// Mantém só o item de índice i de uma sequência.
export const entre = (abre, parser, fecha) => mapear(sequencia(abre, parser, fecha), ([, v]) => v);

// Parser preguiçoso para gramáticas recursivas.
export const preguica = (f) => {
  let parser;
  return (e, p) => (parser ??= f())(e, p);
};

// Associatividade à esquerda: item (op item)*, aplicando f(op, esq, dir).
export const encadearEsq = (item, op, f) => (e, p) => {
  const primeiro = item(e, p);
  if (!primeiro.ok) return primeiro;
  let acc = primeiro.valor;
  p = primeiro.pos;
  for (;;) {
    const o = op(e, p);
    if (!o.ok) break;
    const r = item(e, o.pos);
    if (!r.ok) return r;
    acc = f(o.valor, acc, r.valor);
    p = r.pos;
  }
  return sucesso(acc, p);
};

// Executa o parser exigindo consumir toda a entrada; lança SyntaxError com posição.
export function analisar(parser, entrada) {
  const r = mapear(sequencia(parser, token(fim)), ([v]) => v)(entrada, 0);
  if (!r.ok) throw new SyntaxError(`posição ${r.pos}: esperado ${r.esperado}`);
  return r.valor;
}

// Exemplo pronto: calculadora aritmética com + - * / ^, parênteses e menos unário.
export function calculadora() {
  const numero = token(mapear(regex(/\d+(\.\d+)?/, 'número'), Number));
  const simbolo = (s) => token(literal(s));
  const expr = preguica(() => soma);
  const atomo = ou(numero, entre(simbolo('('), expr, simbolo(')')));
  const unario = preguica(() => ou(mapear(sequencia(simbolo('-'), unario), ([, v]) => -v), potencia));
  const potencia = mapear(
    sequencia(atomo, opcional(sequencia(simbolo('^'), unario))),
    ([base, resto]) => (resto ? base ** resto[1] : base),
  );
  const produto = encadearEsq(unario, ou(simbolo('*'), simbolo('/')), (op, a, b) => (op === '*' ? a * b : a / b));
  const soma = encadearEsq(produto, ou(simbolo('+'), simbolo('-')), (op, a, b) => (op === '+' ? a + b : a - b));
  return (texto) => analisar(soma, texto);
}

// Exemplo pronto: JSON simplificado (null, booleanos, números, strings, arrays, objetos).
export function parserJson() {
  const valor = preguica(() => ou(nulo, booleano, numero, texto, lista, objeto));
  const nulo = mapear(token(literal('null')), () => null);
  const booleano = mapear(token(ou(literal('true'), literal('false'))), (s) => s === 'true');
  const numero = mapear(token(regex(/-?\d+(\.\d+)?([eE][+-]?\d+)?/, 'número')), Number);
  const texto = mapear(token(regex(/"(?:[^"\\]|\\.)*"/, 'string')), (s) => JSON.parse(s));
  const lista = entre(token(literal('[')), separadoPor(valor, token(literal(','))), token(literal(']')));
  const par = mapear(sequencia(texto, token(literal(':')), valor), ([k, , v]) => [k, v]);
  const objeto = mapear(
    entre(token(literal('{')), separadoPor(par, token(literal(','))), token(literal('}'))),
    (pares) => Object.fromEntries(pares),
  );
  return (s) => analisar(valor, s);
}
