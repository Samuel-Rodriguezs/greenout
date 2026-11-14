// Rotulagem de componentes conexos (duas passagens + union-find).
// Primeiro plano = canal R >= 128. Rótulos 1..n; 0 é fundo.

export function rotular(img, conectividade = 4) {
  if (conectividade !== 4 && conectividade !== 8) throw new Error('conectividade deve ser 4 ou 8');
  const l = img.largura;
  const a = img.altura;
  const fg = (x, y) => x >= 0 && y >= 0 && x < l && y < a && img.dados[(y * l + x) * 4] >= 128;
  const rot = new Int32Array(l * a);
  const pai = [0];
  const raiz = (i) => {
    while (pai[i] !== i) {
      pai[i] = pai[pai[i]];
      i = pai[i];
    }
    return i;
  };
  const unir = (u, v) => {
    const ru = raiz(u);
    const rv = raiz(v);
    if (ru !== rv) pai[Math.max(ru, rv)] = Math.min(ru, rv);
  };
  const anteriores = conectividade === 4 ? [[-1, 0], [0, -1]] : [[-1, 0], [0, -1], [-1, -1], [1, -1]];

  for (let y = 0; y < a; y++) {
    for (let x = 0; x < l; x++) {
      if (!fg(x, y)) continue;
      const vizinhos = [];
      for (const [dx, dy] of anteriores) if (fg(x + dx, y + dy)) vizinhos.push(rot[(y + dy) * l + x + dx]);
      if (vizinhos.length === 0) {
        pai.push(pai.length);
        rot[y * l + x] = pai.length - 1;
      } else {
        const m = Math.min(...vizinhos);
        rot[y * l + x] = m;
        for (const v of vizinhos) unir(m, v);
      }
    }
  }

  // Segunda passagem: rótulos consecutivos na ordem de varredura.
  const mapa = new Map();
  const areas = [0];
  for (let i = 0; i < rot.length; i++) {
    if (!rot[i]) continue;
    const r = raiz(rot[i]);
    if (!mapa.has(r)) {
      mapa.set(r, mapa.size + 1);
      areas.push(0);
    }
    rot[i] = mapa.get(r);
    areas[rot[i]]++;
  }
  return { rotulos: rot, quantidade: mapa.size, areas, largura: l, altura: a };
}

// Caixa delimitadora de cada componente: [{rotulo, x0, y0, x1, y1, area}].
export function caixas(resultado) {
  const { rotulos, largura, quantidade, areas } = resultado;
  const c = Array.from({ length: quantidade + 1 }, (_, i) => ({ rotulo: i, x0: Infinity, y0: Infinity, x1: -1, y1: -1, area: areas[i] }));
  for (let i = 0; i < rotulos.length; i++) {
    const r = rotulos[i];
    if (!r) continue;
    const x = i % largura;
    const y = (i - x) / largura;
    c[r].x0 = Math.min(c[r].x0, x);
    c[r].y0 = Math.min(c[r].y0, y);
    c[r].x1 = Math.max(c[r].x1, x);
    c[r].y1 = Math.max(c[r].y1, y);
  }
  return c.slice(1);
}
