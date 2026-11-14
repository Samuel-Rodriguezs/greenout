// Rolagem de dados com parser de notação: "2d6+3", "d20", "4d6kh3", "1d8+1d4-2".

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const TERMO = /^(\d*)d(\d+)(?:(kh|kl)(\d+))?$|^(\d+)$/i;

/**
 * Converte a expressão em termos: {sinal, tipo:'dado', qtd, faces, manter?, quais?}
 * ou {sinal, tipo:'const', valor}.
 */
export function parse(expressao) {
  const texto = expressao.replace(/\s+/g, '');
  if (!texto) throw new Error('expressão vazia');
  const partes = texto.match(/[+-]?[^+-]+/g);
  if (!partes || partes.join('') !== texto) throw new Error('expressão inválida: ' + expressao);
  return partes.map((p, i) => {
    const sinal = p.startsWith('-') ? -1 : 1;
    const corpo = p.replace(/^[+-]/, '');
    if (i > 0 && !/^[+-]/.test(p)) throw new Error('expressão inválida: ' + expressao);
    const m = TERMO.exec(corpo);
    if (!m) throw new Error('termo inválido: ' + corpo);
    if (m[5] !== undefined) return { sinal, tipo: 'const', valor: Number(m[5]) };
    const qtd = m[1] === '' ? 1 : Number(m[1]);
    const faces = Number(m[2]);
    if (qtd < 1 || qtd > 1000) throw new Error('quantidade de dados inválida');
    if (faces < 2) throw new Error('dado precisa ter ao menos 2 faces');
    const termo = { sinal, tipo: 'dado', qtd, faces };
    if (m[3]) {
      const manter = Number(m[4]);
      if (manter < 1 || manter > qtd) throw new Error('quantidade a manter inválida');
      termo.manter = manter;
      termo.quais = m[3].toLowerCase() === 'kh' ? 'maiores' : 'menores';
    }
    return termo;
  });
}

function rolarDado(rng, faces) {
  return Math.floor(rng() * faces) + 1;
}

/** Rola a expressão. Retorna {total, detalhes:[{termo, rolagens, mantidas, subtotal}]}. */
export function rolar(expressao, rng) {
  const termos = parse(expressao);
  let total = 0;
  const detalhes = termos.map((t) => {
    if (t.tipo === 'const') {
      total += t.sinal * t.valor;
      return { termo: t, rolagens: [], mantidas: [], subtotal: t.sinal * t.valor };
    }
    const rolagens = Array.from({ length: t.qtd }, () => rolarDado(rng, t.faces));
    let mantidas = rolagens;
    if (t.manter) {
      const ord = rolagens.slice().sort((a, b) => (t.quais === 'maiores' ? b - a : a - b));
      mantidas = ord.slice(0, t.manter);
    }
    const subtotal = t.sinal * mantidas.reduce((s, v) => s + v, 0);
    total += subtotal;
    return { termo: t, rolagens, mantidas, subtotal };
  });
  return { expressao, total, detalhes };
}

function extremos(t, qual) {
  if (t.tipo === 'const') return t.valor;
  const n = t.manter ?? t.qtd;
  return qual === 'min' ? n : n * t.faces;
}

export function minimo(expressao) {
  return parse(expressao).reduce((s, t) => s + (t.sinal === 1 ? extremos(t, 'min') : -extremos(t, 'max')), 0);
}

export function maximo(expressao) {
  return parse(expressao).reduce((s, t) => s + (t.sinal === 1 ? extremos(t, 'max') : -extremos(t, 'min')), 0);
}

/** Média teórica (apenas sem kh/kl; com kh/kl lança erro). */
export function media(expressao) {
  return parse(expressao).reduce((s, t) => {
    if (t.tipo === 'const') return s + t.sinal * t.valor;
    if (t.manter) throw new Error('média teórica não suportada com kh/kl');
    return s + t.sinal * t.qtd * (t.faces + 1) / 2;
  }, 0);
}
