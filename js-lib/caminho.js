const dividir = (c) => (Array.isArray(c) ? c : String(c).replace(/\[(\w+)\]/g, '.$1').split('.').filter(Boolean));

// Lê valor por caminho ("a.b[0].c"); retorna padrao se ausente.
export function get(obj, caminho, padrao = undefined) {
  let atual = obj;
  for (const k of dividir(caminho)) {
    if (atual == null) return padrao;
    atual = atual[k];
  }
  return atual === undefined ? padrao : atual;
}

// Define valor por caminho, criando objetos/arrays intermediários (muta e retorna obj).
export function set(obj, caminho, valor) {
  const ks = dividir(caminho);
  if (ks.some((k) => k === '__proto__' || k === 'constructor' || k === 'prototype')) return obj;
  let atual = obj;
  ks.forEach((k, i) => {
    if (i === ks.length - 1) { atual[k] = valor; return; }
    if (atual[k] == null || typeof atual[k] !== 'object') atual[k] = /^\d+$/.test(ks[i + 1]) ? [] : {};
    atual = atual[k];
  });
  return obj;
}
