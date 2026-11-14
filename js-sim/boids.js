// Boids simplificado: separação, alinhamento e coesão em mundo toroidal.

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export const PARAMETROS = {
  largura: 100, altura: 100,
  raioVisao: 20, raioSeparacao: 6,
  pesoSeparacao: 0.05, pesoAlinhamento: 0.05, pesoCoesao: 0.005,
  velocidadeMax: 2,
};

export function criarBando(n, rng, largura = 100, altura = 100) {
  return Array.from({ length: n }, () => {
    const ang = rng() * Math.PI * 2;
    return { x: rng() * largura, y: rng() * altura, vx: Math.cos(ang), vy: Math.sin(ang) };
  });
}

/** Menor diferença considerando o mundo toroidal. */
function delta(a, b, tam) {
  let d = b - a;
  if (d > tam / 2) d -= tam;
  else if (d < -tam / 2) d += tam;
  return d;
}

export function limitarVelocidade(b, max) {
  const v = Math.hypot(b.vx, b.vy);
  if (v > max) {
    b.vx = (b.vx / v) * max;
    b.vy = (b.vy / v) * max;
  }
  return b;
}

/** Avança um passo e devolve novo bando (não muta o original). */
export function passo(bando, params = {}) {
  const p = { ...PARAMETROS, ...params };
  return bando.map((b, i) => {
    let sx = 0, sy = 0; // separação
    let ax = 0, ay = 0; // alinhamento
    let cx = 0, cy = 0; // coesão (soma de deslocamentos)
    let vizinhos = 0;
    bando.forEach((o, j) => {
      if (i === j) return;
      const dx = delta(b.x, o.x, p.largura);
      const dy = delta(b.y, o.y, p.altura);
      const dist = Math.hypot(dx, dy);
      if (dist > p.raioVisao) return;
      vizinhos++;
      ax += o.vx; ay += o.vy;
      cx += dx; cy += dy;
      if (dist < p.raioSeparacao && dist > 0) {
        sx -= dx / dist;
        sy -= dy / dist;
      }
    });
    const nb = { ...b };
    if (vizinhos > 0) {
      nb.vx += sx * p.pesoSeparacao + (ax / vizinhos - b.vx) * p.pesoAlinhamento + (cx / vizinhos) * p.pesoCoesao;
      nb.vy += sy * p.pesoSeparacao + (ay / vizinhos - b.vy) * p.pesoAlinhamento + (cy / vizinhos) * p.pesoCoesao;
    }
    limitarVelocidade(nb, p.velocidadeMax);
    nb.x = (((b.x + nb.vx) % p.largura) + p.largura) % p.largura;
    nb.y = (((b.y + nb.vy) % p.altura) + p.altura) % p.altura;
    return nb;
  });
}

export function simular(bando, passos, params) {
  let atual = bando;
  for (let i = 0; i < passos; i++) atual = passo(atual, params);
  return atual;
}

/** Magnitude da velocidade média normalizada (1 = todos alinhados). */
export function ordemDeAlinhamento(bando) {
  let sx = 0, sy = 0, n = 0;
  for (const b of bando) {
    const v = Math.hypot(b.vx, b.vy);
    if (v === 0) continue;
    sx += b.vx / v; sy += b.vy / v; n++;
  }
  return n === 0 ? 0 : Math.hypot(sx, sy) / n;
}
