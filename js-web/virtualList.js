export function visibleWindow({ scrollTop, viewportHeight, itemHeight, total, overscan = 3 }) {
  if (itemHeight <= 0) throw new Error('itemHeight deve ser positivo');
  if (total <= 0) return { start: 0, end: 0, offsetTop: 0, totalHeight: 0, items: 0 };
  const maxScroll = Math.max(0, total * itemHeight - viewportHeight);
  const top = Math.min(Math.max(0, scrollTop), maxScroll);
  const first = Math.floor(top / itemHeight);
  const last = Math.ceil((top + viewportHeight) / itemHeight);
  const start = Math.max(0, first - overscan);
  const end = Math.min(total, last + overscan);
  return { start, end, offsetTop: start * itemHeight, totalHeight: total * itemHeight, items: end - start };
}

// Alturas variáveis: usa soma de prefixos e busca binária.
export function createVariableWindow(heights) {
  const offsets = [0];
  for (const h of heights) offsets.push(offsets[offsets.length - 1] + h);
  const totalHeight = offsets[offsets.length - 1];

  function indexAt(y) {
    let lo = 0;
    let hi = heights.length - 1;
    while (lo < hi) {
      const mid = (lo + hi + 1) >> 1;
      if (offsets[mid] <= y) lo = mid;
      else hi = mid - 1;
    }
    return lo;
  }

  return {
    totalHeight,
    offsetOf: (i) => offsets[i],
    range({ scrollTop, viewportHeight, overscan = 2 }) {
      if (!heights.length) return { start: 0, end: 0, offsetTop: 0, totalHeight };
      const top = Math.min(Math.max(0, scrollTop), Math.max(0, totalHeight - viewportHeight));
      const first = indexAt(top);
      const last = Math.min(heights.length - 1, indexAt(Math.max(top, top + viewportHeight - 1)));
      const start = Math.max(0, first - overscan);
      const end = Math.min(heights.length, last + 1 + overscan);
      return { start, end, offsetTop: offsets[start], totalHeight };
    },
  };
}

export function scrollToIndex(index, { itemHeight, viewportHeight, total, align = 'start' }) {
  const i = Math.min(Math.max(0, index), Math.max(0, total - 1));
  let top = i * itemHeight;
  if (align === 'center') top -= (viewportHeight - itemHeight) / 2;
  else if (align === 'end') top -= viewportHeight - itemHeight;
  return Math.min(Math.max(0, top), Math.max(0, total * itemHeight - viewportHeight));
}
