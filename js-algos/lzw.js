// Compressão LZW sobre strings (dicionário inicial: código UTF-16 de 0 a 255 não é
// suficiente, então o dicionário parte dos caracteres vistos em uma primeira passada).

// Codifica: devolve { alfabeto, codigos }. O alfabeto viaja junto para permitir decodificar.
export function lzwCodificar(texto) {
  const alfabeto = [...new Set(texto)].sort();
  const dic = new Map(alfabeto.map((c, i) => [c, i]));
  const codigos = [];
  let w = '';
  for (const c of texto) {
    const wc = w + c;
    if (dic.has(wc)) { w = wc; continue; }
    codigos.push(dic.get(w));
    dic.set(wc, dic.size);
    w = c;
  }
  if (w !== '') codigos.push(dic.get(w));
  return { alfabeto, codigos };
}

export function lzwDecodificar({ alfabeto, codigos }) {
  if (codigos.length === 0) return '';
  const dic = [...alfabeto];
  let w = dic[codigos[0]];
  if (w === undefined) throw new RangeError(`código inválido: ${codigos[0]}`);
  let saida = w;
  for (let i = 1; i < codigos.length; i++) {
    const k = codigos[i];
    let entrada;
    if (k < dic.length) entrada = dic[k];
    else if (k === dic.length) entrada = w + [...w][0]; // caso especial cScSc
    else throw new RangeError(`código inválido: ${k}`);
    saida += entrada;
    dic.push(w + [...entrada][0]);
    w = entrada;
  }
  return saida;
}
