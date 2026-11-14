const norm = (s) => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

// Retorna null se não casar; senão { score, indices }.
export function fuzzyMatch(query, text) {
  const q = norm(query);
  const t = norm(text);
  if (!q) return { score: 0, indices: [] };
  const indices = [];
  let ti = 0;
  let score = 0;
  let prev = -2;
  for (const ch of q) {
    const found = t.indexOf(ch, ti);
    if (found === -1) return null;
    indices.push(found);
    score += 1;
    if (found === prev + 1) score += 5; // sequência consecutiva
    const before = t[found - 1];
    if (found === 0) score += 8; // início do texto
    else if (before === ' ' || before === '-' || before === '_' || before === '/' || before === '.') score += 6; // início de palavra
    score -= Math.min(3, (found - ti) * 0.25); // penaliza saltos
    prev = found;
    ti = found + 1;
  }
  if (t === q) score += 20;
  else if (t.startsWith(q)) score += 10;
  score -= (t.length - q.length) * 0.05; // prefere textos curtos
  return { score, indices };
}

export function fuzzySearch(query, items, { key = (x) => x, limit = Infinity } = {}) {
  const out = [];
  items.forEach((item, order) => {
    const m = fuzzyMatch(query, key(item));
    if (m) out.push({ item, score: m.score, indices: m.indices, order });
  });
  out.sort((a, b) => b.score - a.score || a.order - b.order);
  return out.slice(0, limit);
}

export function highlight(text, indices, open = '<mark>', close = '</mark>') {
  // indices referem-se ao texto normalizado, que preserva o comprimento em NFD->sem marcas apenas para texto já composto;
  // para segurança, mapeia por caracteres base.
  const chars = [...String(text)];
  const baseIdx = [];
  chars.forEach((c, i) => { if (norm(c).length) baseIdx.push(i); });
  const marks = new Set(indices.map((i) => baseIdx[i]));
  let out = '';
  let on = false;
  chars.forEach((c, i) => {
    const m = marks.has(i);
    if (m && !on) { out += open; on = true; }
    if (!m && on) { out += close; on = false; }
    out += c;
  });
  return on ? out + close : out;
}
