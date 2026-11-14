// debounce e throttle. Aceitam um `timers` injetável para facilitar testes.

const timersPadrao = { setTimeout, clearTimeout };

/** Adia a chamada até `espera` ms sem novas chamadas. Possui `.cancelar()`. */
export function debounce(fn, espera, timers = timersPadrao) {
  let id = null;
  const debounced = function (...args) {
    if (id !== null) timers.clearTimeout(id);
    id = timers.setTimeout(() => {
      id = null;
      fn.apply(this, args);
    }, espera);
  };
  debounced.cancelar = () => {
    if (id !== null) timers.clearTimeout(id);
    id = null;
  };
  return debounced;
}

/**
 * Executa `fn` no máximo uma vez a cada `intervalo` ms.
 * Chama imediatamente (leading) e, se houve chamadas no intervalo,
 * dispara uma última com os argumentos mais recentes (trailing).
 */
export function throttle(fn, intervalo, timers = timersPadrao) {
  let id = null;
  let pendente = null;
  const executar = (ctx, args) => {
    fn.apply(ctx, args);
    id = timers.setTimeout(() => {
      id = null;
      if (pendente) {
        const { ctx: c, args: a } = pendente;
        pendente = null;
        executar(c, a);
      }
    }, intervalo);
  };
  return function (...args) {
    if (id === null) executar(this, args);
    else pendente = { ctx: this, args };
  };
}
