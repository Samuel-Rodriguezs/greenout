// Memoização com resolvedor de chave customizável e cache inspecionável.

export function memoize(fn, resolverChave = (...args) => JSON.stringify(args)) {
  const cache = new Map();
  const memoizada = function (...args) {
    const chave = resolverChave(...args);
    if (cache.has(chave)) return cache.get(chave);
    const resultado = fn.apply(this, args);
    cache.set(chave, resultado);
    return resultado;
  };
  memoizada.cache = cache;
  return memoizada;
}

/** Versão para funções assíncronas: não cacheia rejeições. */
export function memoizeAsync(fn, resolverChave = (...args) => JSON.stringify(args)) {
  const cache = new Map();
  return function (...args) {
    const chave = resolverChave(...args);
    if (cache.has(chave)) return cache.get(chave);
    const promessa = Promise.resolve(fn.apply(this, args)).catch((erro) => {
      cache.delete(chave);
      throw erro;
    });
    cache.set(chave, promessa);
    return promessa;
  };
}
