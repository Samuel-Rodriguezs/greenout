// compose (direita para esquerda) e pipe (esquerda para direita), síncronos e assíncronos.

function validar(fns) {
  fns.forEach((f) => {
    if (typeof f !== 'function') throw new TypeError('todos os argumentos devem ser funções');
  });
}

export function pipe(...fns) {
  validar(fns);
  return function (...args) {
    if (fns.length === 0) return args[0];
    const [primeira, ...resto] = fns;
    return resto.reduce((acc, f) => f.call(this, acc), primeira.apply(this, args));
  };
}

export function compose(...fns) {
  validar(fns);
  return pipe(...[...fns].reverse());
}

/** pipe que aguarda cada etapa (aceita funções assíncronas). */
export function pipeAsync(...fns) {
  validar(fns);
  return async function (...args) {
    if (fns.length === 0) return args[0];
    const [primeira, ...resto] = fns;
    let acc = await primeira.apply(this, args);
    for (const f of resto) acc = await f.call(this, acc);
    return acc;
  };
}
