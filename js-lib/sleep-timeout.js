export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class TimeoutError extends Error {
  constructor(ms) { super(`Tempo esgotado após ${ms}ms`); this.name = 'TimeoutError'; }
}

// Rejeita com TimeoutError se a promessa não resolver em `ms`.
export function comTimeout(promessa, ms) {
  let timer;
  const limite = new Promise((_, rej) => { timer = setTimeout(() => rej(new TimeoutError(ms)), ms); });
  return Promise.race([promessa, limite]).finally(() => clearTimeout(timer));
}
