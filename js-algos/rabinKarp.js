// Rabin-Karp com hash rolante (aritmética BigInt-free via módulo primo pequeno).
const BASE = 257;
const MOD = 1_000_000_007;

// Todas as posições onde padrao ocorre em texto; confirma cada candidato (evita falso positivo).
export function rabinKarp(texto, padrao) {
  const n = texto.length, m = padrao.length;
  if (m === 0 || m > n) return [];
  // BASE^(m-1) mod MOD; produtos < 2^53 porque BASE*MOD < 2^53
  let potencia = 1;
  for (let i = 1; i < m; i++) potencia = (potencia * BASE) % MOD;
  let hp = 0, ht = 0;
  for (let i = 0; i < m; i++) {
    hp = (hp * BASE + padrao.charCodeAt(i)) % MOD;
    ht = (ht * BASE + texto.charCodeAt(i)) % MOD;
  }
  const achados = [];
  for (let i = 0; ; i++) {
    if (hp === ht && texto.startsWith(padrao, i)) achados.push(i);
    if (i + m >= n) break;
    ht = (ht - texto.charCodeAt(i) * potencia % MOD + MOD) % MOD;
    ht = (ht * BASE + texto.charCodeAt(i + m)) % MOD;
  }
  return achados;
}

// Busca de vários padrões de mesmo tamanho: { padrao: [posições] }.
export function rabinKarpMultiplo(texto, padroes) {
  const res = {};
  for (const p of padroes) res[p] = rabinKarp(texto, p);
  return res;
}
