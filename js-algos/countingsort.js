// Counting sort estável para inteiros, com chave opcional.
export function countingsort(arr, chave = (x) => x) {
  if (arr.length === 0) return [];
  const chaves = arr.map(chave);
  for (const k of chaves) {
    if (!Number.isInteger(k)) throw new TypeError(`chave não inteira: ${k}`);
  }
  let min = chaves[0], max = chaves[0];
  for (const k of chaves) { if (k < min) min = k; if (k > max) max = k; }
  const cont = new Array(max - min + 2).fill(0);
  for (const k of chaves) cont[k - min + 1]++;
  for (let i = 1; i < cont.length; i++) cont[i] += cont[i - 1];
  const saida = new Array(arr.length);
  for (let i = 0; i < arr.length; i++) saida[cont[chaves[i] - min]++] = arr[i];
  return saida;
}
