export function moveItem(list, from, to) {
  if (from < 0 || from >= list.length) throw new RangeError('Índice de origem inválido');
  const dest = Math.min(Math.max(0, to), list.length - 1);
  const copy = [...list];
  const [item] = copy.splice(from, 1);
  copy.splice(dest, 0, item);
  return copy;
}

// Dado o Y do ponteiro e as alturas dos itens, calcula o índice de destino
// (ponto médio do item como limiar).
export function dropIndex(pointerY, heights, { originTop = 0 } = {}) {
  let top = originTop;
  for (let i = 0; i < heights.length; i++) {
    if (pointerY < top + heights[i] / 2) return i;
    top += heights[i];
  }
  return heights.length - 1;
}

// Reordena por ids; ids ausentes em `novaOrdem` vão para o fim mantendo ordem relativa.
export function reorderByIds(items, novaOrdem, idOf = (x) => x.id) {
  const byId = new Map(items.map((i) => [idOf(i), i]));
  const out = [];
  for (const id of novaOrdem) {
    if (byId.has(id)) {
      out.push(byId.get(id));
      byId.delete(id);
    }
  }
  return [...out, ...byId.values()];
}

// Move vários itens selecionados para uma posição, preservando a ordem relativa.
export function moveMany(list, indices, to) {
  const sel = [...new Set(indices)].filter((i) => i >= 0 && i < list.length).sort((a, b) => a - b);
  const moved = sel.map((i) => list[i]);
  const rest = list.filter((_, i) => !sel.includes(i));
  const antes = sel.filter((i) => i < to).length;
  const pos = Math.min(Math.max(0, to - antes), rest.length);
  return [...rest.slice(0, pos), ...moved, ...rest.slice(pos)];
}

// Posições fracionárias (estilo "fractional indexing" simples) para evitar reindexar tudo.
export function positionBetween(before, after) {
  if (before == null && after == null) return 1;
  if (before == null) return after / 2;
  if (after == null) return before + 1;
  return (before + after) / 2;
}

export function previewOrder(list, from, hoverIndex) {
  return moveItem(list, from, hoverIndex).map((item, i) => ({ item, index: i, moved: item === list[from] }));
}
