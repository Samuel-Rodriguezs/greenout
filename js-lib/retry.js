const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

// Tenta executar fn até `tentativas` vezes com backoff exponencial (base * fator^n).
export async function retry(fn, { tentativas = 3, base = 100, fator = 2, max = 30000, esperar = dormir } = {}) {
  let ultimo;
  for (let i = 0; i < tentativas; i++) {
    try {
      return await fn(i);
    } catch (e) {
      ultimo = e;
      if (i < tentativas - 1) await esperar(Math.min(max, base * fator ** i));
    }
  }
  throw ultimo;
}
