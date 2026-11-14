// Limita a concorrência de tarefas assíncronas.
export function pLimit(concorrencia) {
  if (!Number.isInteger(concorrencia) || concorrencia < 1) throw new RangeError('concorrência deve ser >= 1');
  let ativos = 0;
  const fila = [];
  const proximo = () => {
    if (ativos >= concorrencia || fila.length === 0) return;
    ativos++;
    const { fn, resolve, reject } = fila.shift();
    Promise.resolve().then(fn).then(resolve, reject).finally(() => { ativos--; proximo(); });
  };
  return (fn) => new Promise((resolve, reject) => { fila.push({ fn, resolve, reject }); proximo(); });
}
