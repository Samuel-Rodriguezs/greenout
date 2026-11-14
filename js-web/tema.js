export function hexParaRgb(hex) {
  let h = String(hex).trim().replace(/^#/, '');
  if (h.length === 3) h = [...h].map((c) => c + c).join('');
  if (!/^[0-9a-fA-F]{6}$/.test(h)) throw new Error(`Cor inválida: ${hex}`);
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

export const rgbParaHex = (rgb) =>
  '#' + rgb.map((c) => Math.round(Math.min(255, Math.max(0, c))).toString(16).padStart(2, '0')).join('');

export function luminancia(hex) {
  const [r, g, b] = hexParaRgb(hex).map((v) => {
    const c = v / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

export function contraste(a, b) {
  const [l1, l2] = [luminancia(a), luminancia(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

export function nivelWCAG(fg, bg, { grande = false } = {}) {
  const r = contraste(fg, bg);
  if (r >= 7 || (grande && r >= 4.5)) return 'AAA';
  if (r >= 4.5 || (grande && r >= 3)) return 'AA';
  return 'falha';
}

export function corLegivel(bg, claro = '#ffffff', escuro = '#000000') {
  return contraste(claro, bg) >= contraste(escuro, bg) ? claro : escuro;
}

export function misturar(a, b, peso = 0.5) {
  const ra = hexParaRgb(a);
  const rb = hexParaRgb(b);
  return rgbParaHex(ra.map((v, i) => v * (1 - peso) + rb[i] * peso));
}

export const clarear = (hex, p) => misturar(hex, '#ffffff', p);
export const escurecer = (hex, p) => misturar(hex, '#000000', p);

// Escurece/clareia o texto até atingir a razão mínima de contraste com o fundo.
export function ajustarParaContraste(fg, bg, minimo = 4.5) {
  if (contraste(fg, bg) >= minimo) return fg;
  const alvo = luminancia(bg) > 0.5 ? '#000000' : '#ffffff';
  for (let p = 0.05; p <= 1.0001; p += 0.05) {
    const c = misturar(fg, alvo, p);
    if (contraste(c, bg) >= minimo) return c;
  }
  return alvo;
}

export function createTemaManager({ temas, inicial, onChange = () => {} }) {
  let atual = inicial in temas ? inicial : Object.keys(temas)[0];
  return {
    get atual() { return atual; },
    get cores() { return temas[atual]; },
    definir(nome) {
      if (!(nome in temas)) throw new Error(`Tema desconhecido: ${nome}`);
      atual = nome;
      onChange(nome, temas[nome]);
    },
    alternar() {
      const nomes = Object.keys(temas);
      this.definir(nomes[(nomes.indexOf(atual) + 1) % nomes.length]);
    },
    auditar(pares = [['texto', 'fundo']]) {
      return pares.map(([f, b]) => ({ par: [f, b], razao: contraste(temas[atual][f], temas[atual][b]), nivel: nivelWCAG(temas[atual][f], temas[atual][b]) }));
    },
    // Respeita prefers-color-scheme sem acessar o DOM: recebe o booleano de fora
    seguirSistema(escuro, { claro = 'claro', noturno = 'escuro' } = {}) {
      this.definir(escuro ? noturno : claro);
    },
  };
}
