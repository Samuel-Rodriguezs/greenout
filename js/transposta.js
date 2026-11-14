// Matriz transposta e utilitários relacionados.

function validarMatriz(m) {
  if (!Array.isArray(m) || !m.every(Array.isArray)) {
    throw new TypeError('matriz deve ser um array de arrays');
  }
  if (m.length > 0 && !m.every((linha) => linha.length === m[0].length)) {
    throw new RangeError('todas as linhas devem ter o mesmo tamanho');
  }
}

export function transpor(matriz) {
  validarMatriz(matriz);
  if (matriz.length === 0) return [];
  return matriz[0].map((_, j) => matriz.map((linha) => linha[j]));
}

export function ehSimetrica(matriz) {
  validarMatriz(matriz);
  if (matriz.length !== (matriz[0]?.length ?? 0)) return false;
  return matriz.every((linha, i) => linha.every((v, j) => Object.is(v, matriz[j][i])));
}

/** Rotaciona 90 graus no sentido horário (transpor + inverter cada linha). */
export function rotacionarHorario(matriz) {
  return transpor(matriz).map((linha) => linha.reverse());
}
