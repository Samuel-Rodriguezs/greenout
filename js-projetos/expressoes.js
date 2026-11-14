// Tokenizer + parser (descida recursiva) + avaliador de expressões aritméticas.
// Suporta + - * / ^ (associativo à direita), parênteses, unário, variáveis e funções.

export function tokenizar(texto) {
  const tokens = [];
  const re = /\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_]\w*)|(.))/gy;
  let m;
  while (re.lastIndex < texto.length && (m = re.exec(texto))) {
    if (m[1] !== undefined) tokens.push({ tipo: 'num', valor: Number(m[1]) });
    else if (m[2] !== undefined) tokens.push({ tipo: 'id', valor: m[2] });
    else if ('+-*/^(),'.includes(m[3])) tokens.push({ tipo: 'op', valor: m[3] });
    else throw new SyntaxError(`Caractere inesperado: ${m[3]}`);
  }
  return tokens;
}

export function parse(texto) {
  const tokens = tokenizar(texto);
  let pos = 0;
  const olhar = () => tokens[pos];
  const ehOp = (v) => olhar()?.tipo === 'op' && olhar().valor === v;
  const consumir = (v) => {
    if (!ehOp(v)) throw new SyntaxError(`Esperado '${v}'`);
    pos++;
  };

  function expressao() {
    let esq = termo();
    while (ehOp('+') || ehOp('-')) {
      const op = tokens[pos++].valor;
      esq = { tipo: 'bin', op, esq, dir: termo() };
    }
    return esq;
  }
  function termo() {
    let esq = unario();
    while (ehOp('*') || ehOp('/')) {
      const op = tokens[pos++].valor;
      esq = { tipo: 'bin', op, esq, dir: unario() };
    }
    return esq;
  }
  function unario() {
    if (ehOp('-')) {
      pos++;
      return { tipo: 'neg', arg: unario() };
    }
    return potencia();
  }
  function potencia() {
    const base = primario();
    if (ehOp('^')) {
      pos++;
      return { tipo: 'bin', op: '^', esq: base, dir: unario() };
    }
    return base;
  }
  function primario() {
    const t = tokens[pos++];
    if (!t) throw new SyntaxError('Fim inesperado da expressão');
    if (t.tipo === 'num') return { tipo: 'num', valor: t.valor };
    if (t.tipo === 'id') {
      if (ehOp('(')) {
        pos++;
        const args = [];
        if (!ehOp(')')) {
          do args.push(expressao()); while (ehOp(',') && ++pos);
        }
        consumir(')');
        return { tipo: 'chamada', nome: t.valor, args };
      }
      return { tipo: 'var', nome: t.valor };
    }
    if (t.valor === '(') {
      const e = expressao();
      consumir(')');
      return e;
    }
    throw new SyntaxError(`Token inesperado: ${t.valor}`);
  }

  const arvore = expressao();
  if (pos < tokens.length) throw new SyntaxError(`Token inesperado: ${tokens[pos].valor}`);
  return arvore;
}

const FUNCOES = { raiz: Math.sqrt, abs: Math.abs, max: Math.max, min: Math.min, arredonda: Math.round };

export function avaliar(no, vars = {}) {
  switch (no.tipo) {
    case 'num': return no.valor;
    case 'var':
      if (!(no.nome in vars)) throw new ReferenceError(`Variável indefinida: ${no.nome}`);
      return vars[no.nome];
    case 'neg': return -avaliar(no.arg, vars);
    case 'chamada': {
      const f = FUNCOES[no.nome];
      if (!f) throw new ReferenceError(`Função desconhecida: ${no.nome}`);
      return f(...no.args.map((a) => avaliar(a, vars)));
    }
    case 'bin': {
      const a = avaliar(no.esq, vars);
      const b = avaliar(no.dir, vars);
      if (no.op === '+') return a + b;
      if (no.op === '-') return a - b;
      if (no.op === '*') return a * b;
      if (no.op === '^') return a ** b;
      if (b === 0) throw new RangeError('Divisão por zero');
      return a / b;
    }
    default: throw new Error(`Nó desconhecido: ${no.tipo}`);
  }
}

export function calcular(texto, vars) {
  return avaliar(parse(texto), vars);
}
