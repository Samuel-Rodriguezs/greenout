// Divide um array em blocos de tamanho fixo.
export function chunk(lista, tamanho) {
  if (!Number.isInteger(tamanho) || tamanho < 1) throw new RangeError('tamanho deve ser inteiro >= 1');
  const blocos = [];
  for (let i = 0; i < lista.length; i += tamanho) blocos.push(lista.slice(i, i + tamanho));
  return blocos;
}
