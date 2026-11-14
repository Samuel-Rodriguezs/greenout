// Clone profundo com suporte a Date, RegExp, Map, Set, arrays e referências circulares.

export function deepClone(valor, vistos = new WeakMap()) {
  if (valor === null || typeof valor !== 'object') return valor;
  if (vistos.has(valor)) return vistos.get(valor);

  if (valor instanceof Date) return new Date(valor.getTime());
  if (valor instanceof RegExp) {
    const r = new RegExp(valor.source, valor.flags);
    r.lastIndex = valor.lastIndex;
    return r;
  }
  if (valor instanceof Map) {
    const copia = new Map();
    vistos.set(valor, copia);
    valor.forEach((v, k) => copia.set(deepClone(k, vistos), deepClone(v, vistos)));
    return copia;
  }
  if (valor instanceof Set) {
    const copia = new Set();
    vistos.set(valor, copia);
    valor.forEach((v) => copia.add(deepClone(v, vistos)));
    return copia;
  }
  if (Array.isArray(valor)) {
    const copia = new Array(valor.length);
    vistos.set(valor, copia);
    valor.forEach((v, i) => { copia[i] = deepClone(v, vistos); });
    return copia;
  }

  const copia = Object.create(Object.getPrototypeOf(valor));
  vistos.set(valor, copia);
  for (const chave of Reflect.ownKeys(valor)) {
    copia[chave] = deepClone(valor[chave], vistos);
  }
  return copia;
}
