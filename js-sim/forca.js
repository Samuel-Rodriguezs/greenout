// Jogo da forca: lógica pura, com sorteio via PRNG injetável.

/** PRNG mulberry32: retorna função que gera números em [0,1). */
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

/** Remove acentos e converte para minúsculas. */
export function normalizar(texto) {
  return texto.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
}

export function escolherPalavra(lista, rng) {
  if (lista.length === 0) throw new Error('lista vazia');
  return lista[Math.floor(rng() * lista.length)];
}

export function criarJogo(palavra, maxErros = 6) {
  return { palavra, maxErros, acertos: [], erros: [], status: 'jogando' };
}

/** Chuta uma letra e devolve o novo estado (imutável). */
export function chutar(jogo, letra) {
  if (jogo.status !== 'jogando') return jogo;
  const l = normalizar(letra);
  if (l.length !== 1 || !/[a-z]/.test(l)) throw new Error('chute inválido: ' + letra);
  if (jogo.acertos.includes(l) || jogo.erros.includes(l)) return jogo;

  const alvo = normalizar(jogo.palavra);
  const acertou = alvo.includes(l);
  const acertos = acertou ? [...jogo.acertos, l] : jogo.acertos;
  const erros = acertou ? jogo.erros : [...jogo.erros, l];

  let status = 'jogando';
  const completa = [...alvo].every((c) => !/[a-z]/.test(c) || acertos.includes(c));
  if (completa) status = 'venceu';
  else if (erros.length >= jogo.maxErros) status = 'perdeu';
  return { ...jogo, acertos, erros, status };
}

/** Palavra mascarada, ex.: "c _ s a". */
export function mascara(jogo) {
  return [...jogo.palavra]
    .map((c) => {
      const n = normalizar(c);
      return !/[a-z]/.test(n) || jogo.acertos.includes(n) ? c : '_';
    })
    .join(' ');
}
