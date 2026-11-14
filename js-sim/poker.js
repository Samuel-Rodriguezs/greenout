// Baralho de 52 cartas e avaliador de mão de poker (5 cartas; melhor mão entre 5 a 7).

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

export const NAIPES = ['c', 'd', 'h', 's']; // paus, ouros, copas, espadas
const SIMBOLOS = { 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A' };

export const CATEGORIAS = [
  'Carta alta', 'Par', 'Dois pares', 'Trinca', 'Sequência',
  'Flush', 'Full house', 'Quadra', 'Straight flush', 'Royal flush',
];

export function criarBaralho() {
  const b = [];
  for (const naipe of NAIPES) for (let valor = 2; valor <= 14; valor++) b.push({ valor, naipe });
  return b;
}

export function embaralhar(baralho, rng) {
  const a = baralho.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/** Distribui n cartas do topo; devolve {mao, resto}. */
export function distribuir(baralho, n) {
  if (n > baralho.length) throw new Error('baralho sem cartas suficientes');
  return { mao: baralho.slice(0, n), resto: baralho.slice(n) };
}

/** "As" -> {valor:14, naipe:'s'}; aceita "10h" e "Th". */
export function parseCarta(texto) {
  const m = /^(10|[2-9TJQKA])([cdhs])$/i.exec(texto.trim());
  if (!m) throw new Error('carta inválida: ' + texto);
  const v = m[1].toUpperCase();
  const valor = v === '10' || v === 'T' ? 10 : { J: 11, Q: 12, K: 13, A: 14 }[v] ?? Number(v);
  return { valor, naipe: m[2].toLowerCase() };
}

export function parseMao(texto) {
  return texto.trim().split(/\s+/).map(parseCarta);
}

export function formatarCarta(c) {
  return (SIMBOLOS[c.valor] ?? String(c.valor)) + c.naipe;
}

/** Avalia exatamente 5 cartas. Retorna {categoria, nome, desempate}. */
export function avaliarMao(cartas) {
  if (cartas.length !== 5) throw new Error('a mão deve ter 5 cartas');
  const valores = cartas.map((c) => c.valor).sort((a, b) => b - a);
  const flush = cartas.every((c) => c.naipe === cartas[0].naipe);

  const contagem = new Map();
  for (const v of valores) contagem.set(v, (contagem.get(v) ?? 0) + 1);
  // grupos ordenados por quantidade e depois valor (desc)
  const grupos = [...contagem.entries()].sort((a, b) => b[1] - a[1] || b[0] - a[0]);
  const padrao = grupos.map((g) => g[1]).join('');
  const desempateGrupos = grupos.map((g) => g[0]);

  let altaSequencia = 0;
  if (contagem.size === 5) {
    if (valores[0] - valores[4] === 4) altaSequencia = valores[0];
    else if (valores.join() === '14,5,4,3,2') altaSequencia = 5; // roda A-2-3-4-5
  }

  let categoria;
  let desempate = desempateGrupos;
  if (altaSequencia && flush) {
    categoria = altaSequencia === 14 ? 9 : 8;
    desempate = [altaSequencia];
  } else if (padrao === '41') categoria = 7;
  else if (padrao === '32') categoria = 6;
  else if (flush) { categoria = 5; desempate = valores; }
  else if (altaSequencia) { categoria = 4; desempate = [altaSequencia]; }
  else if (padrao === '311') categoria = 3;
  else if (padrao === '221') categoria = 2;
  else if (padrao === '2111') categoria = 1;
  else { categoria = 0; desempate = valores; }

  return { categoria, nome: CATEGORIAS[categoria], desempate };
}

/** >0 se a vence, <0 se b vence, 0 empate. Aceita resultados de avaliarMao. */
export function compararAvaliacoes(a, b) {
  if (a.categoria !== b.categoria) return a.categoria - b.categoria;
  for (let i = 0; i < Math.max(a.desempate.length, b.desempate.length); i++) {
    const d = (a.desempate[i] ?? 0) - (b.desempate[i] ?? 0);
    if (d !== 0) return d;
  }
  return 0;
}

export function compararMaos(a, b) {
  return compararAvaliacoes(avaliarMao(a), avaliarMao(b));
}

function combinacoes(lista, k, inicio = 0, atual = [], saida = []) {
  if (atual.length === k) {
    saida.push(atual.slice());
    return saida;
  }
  for (let i = inicio; i < lista.length; i++) {
    atual.push(lista[i]);
    combinacoes(lista, k, i + 1, atual, saida);
    atual.pop();
  }
  return saida;
}

/** Melhor mão de 5 cartas dentre 5 a 7 cartas. */
export function melhorMao(cartas) {
  if (cartas.length < 5 || cartas.length > 7) throw new Error('use de 5 a 7 cartas');
  let melhor = null;
  for (const c of combinacoes(cartas, 5)) {
    const av = avaliarMao(c);
    if (!melhor || compararAvaliacoes(av, melhor.avaliacao) > 0) melhor = { cartas: c, avaliacao: av };
  }
  return melhor;
}
