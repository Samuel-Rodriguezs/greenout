const collator = new Intl.Collator('pt-BR', { sensitivity: 'base', numeric: true });

function compareValues(a, b) {
  if (a == null && b == null) return 0;
  if (a == null) return 1;
  if (b == null) return -1;
  if (typeof a === 'number' && typeof b === 'number') return a - b;
  if (a instanceof Date && b instanceof Date) return a - b;
  return collator.compare(String(a), String(b));
}

// sorts: [{ key, dir: 'asc'|'desc' }, ...] — ordenação estável multi-coluna
export function sortRows(rows, sorts = []) {
  if (!sorts.length) return [...rows];
  return rows
    .map((row, i) => ({ row, i }))
    .sort((x, y) => {
      for (const { key, dir = 'asc' } of sorts) {
        const c = compareValues(x.row[key], y.row[key]);
        if (c !== 0) return dir === 'desc' ? -c : c;
      }
      return x.i - y.i;
    })
    .map((e) => e.row);
}

export function toggleSort(sorts, key) {
  const cur = sorts.find((s) => s.key === key);
  if (!cur) return [{ key, dir: 'asc' }];
  if (cur.dir === 'asc') return [{ key, dir: 'desc' }];
  return [];
}

export function paginate(rows, page = 1, pageSize = 10) {
  if (pageSize < 1) throw new Error('pageSize deve ser >= 1');
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const current = Math.min(Math.max(1, page), totalPages);
  const start = (current - 1) * pageSize;
  return {
    rows: rows.slice(start, start + pageSize),
    page: current,
    pageSize,
    total: rows.length,
    totalPages,
    hasPrev: current > 1,
    hasNext: current < totalPages,
  };
}

// Janela de números de página com reticências: [1, '…', 4, 5, 6, '…', 10]
export function pageNumbers(current, totalPages, siblings = 1) {
  const first = 1;
  const keep = new Set([first, totalPages]);
  for (let i = current - siblings; i <= current + siblings; i++) {
    if (i >= first && i <= totalPages) keep.add(i);
  }
  const sorted = [...keep].sort((a, b) => a - b);
  const out = [];
  sorted.forEach((n, i) => {
    if (i > 0) {
      const gap = n - sorted[i - 1];
      if (gap === 2) out.push(n - 1);
      else if (gap > 2) out.push('…');
    }
    out.push(n);
  });
  return out;
}

export function tableView(rows, { sorts = [], page = 1, pageSize = 10, filter = null } = {}) {
  const filtered = filter ? rows.filter(filter) : rows;
  return paginate(sortRows(filtered, sorts), page, pageSize);
}
