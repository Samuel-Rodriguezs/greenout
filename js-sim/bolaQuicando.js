// Física de uma bola quicando numa caixa (eixo y para baixo), integração semi-implícita de Euler.

export function criarBola({ x = 0, y = 0, vx = 0, vy = 0, raio = 1, restituicao = 0.8 } = {}) {
  return { x, y, vx, vy, raio, restituicao };
}

export const MUNDO_PADRAO = { largura: 100, altura: 100, gravidade: 9.8, atritoChao: 0.9, limiarRepouso: 0.5 };

/** Avança dt segundos; devolve nova bola. Colisões com paredes, teto e chão. */
export function passo(bola, dt, mundo = {}) {
  const m = { ...MUNDO_PADRAO, ...mundo };
  let { x, y, vx, vy } = bola;
  const { raio, restituicao } = bola;

  vy += m.gravidade * dt;
  x += vx * dt;
  y += vy * dt;

  if (x - raio < 0) { x = raio; vx = Math.abs(vx) * restituicao; }
  else if (x + raio > m.largura) { x = m.largura - raio; vx = -Math.abs(vx) * restituicao; }

  if (y - raio < 0) { y = raio; vy = Math.abs(vy) * restituicao; }
  const chao = m.altura - raio;
  if (y > chao) {
    y = chao;
    vy = -Math.abs(vy) * restituicao;
    vx *= m.atritoChao; // atrito no contato
    if (Math.abs(vy) < m.limiarRepouso) vy = 0;
  }
  return { ...bola, x, y, vx, vy };
}

export function simular(bola, dt, passos, mundo) {
  let b = bola;
  for (let i = 0; i < passos; i++) b = passo(b, dt, mundo);
  return b;
}

/** Energia mecânica por unidade de massa (altura medida a partir do chão). */
export function energia(bola, mundo = {}) {
  const m = { ...MUNDO_PADRAO, ...mundo };
  const h = m.altura - bola.raio - bola.y;
  return 0.5 * (bola.vx ** 2 + bola.vy ** 2) + m.gravidade * h;
}

export function emRepouso(bola, mundo = {}) {
  const m = { ...MUNDO_PADRAO, ...mundo };
  return bola.vy === 0 && Math.abs(bola.y - (m.altura - bola.raio)) < 1e-9;
}
