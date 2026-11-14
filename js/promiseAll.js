// Implementação manual de Promise.all e Promise.allSettled.

/** Resolve com array de resultados na ordem original; rejeita na primeira falha. */
export function promiseAll(itens) {
  return new Promise((resolve, reject) => {
    const lista = Array.from(itens);
    const resultados = new Array(lista.length);
    let restantes = lista.length;
    if (restantes === 0) {
      resolve(resultados);
      return;
    }
    lista.forEach((item, i) => {
      Promise.resolve(item).then((valor) => {
        resultados[i] = valor;
        restantes -= 1;
        if (restantes === 0) resolve(resultados);
      }, reject);
    });
  });
}

/** Nunca rejeita: devolve {status, value|reason} para cada item. */
export function promiseAllSettled(itens) {
  return promiseAll(
    Array.from(itens, (item) =>
      Promise.resolve(item).then(
        (value) => ({ status: 'fulfilled', value }),
        (reason) => ({ status: 'rejected', reason }),
      ),
    ),
  );
}
