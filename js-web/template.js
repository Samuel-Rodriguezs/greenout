const esc = (v) =>
  String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function tokenize(src) {
  const tokens = [];
  const re = /\{\{\{([\s\S]+?)\}\}\}|\{\{([\s\S]+?)\}\}/g;
  let last = 0;
  let m;
  while ((m = re.exec(src))) {
    if (m.index > last) tokens.push({ type: 'text', value: src.slice(last, m.index) });
    if (m[1] !== undefined) tokens.push({ type: 'raw', value: m[1].trim() });
    else {
      const body = m[2].trim();
      if (body.startsWith('#if ')) tokens.push({ type: 'if', value: body.slice(4).trim() });
      else if (body.startsWith('#each ')) tokens.push({ type: 'each', value: body.slice(6).trim() });
      else if (body === 'else') tokens.push({ type: 'else' });
      else if (body === '/if' || body === '/each') tokens.push({ type: 'end', value: body.slice(1) });
      else tokens.push({ type: 'var', value: body });
    }
    last = re.lastIndex;
  }
  if (last < src.length) tokens.push({ type: 'text', value: src.slice(last) });
  return tokens;
}

function parse(tokens) {
  let i = 0;
  function block(until) {
    const out = [];
    while (i < tokens.length) {
      const t = tokens[i];
      if (t.type === 'end' || t.type === 'else') {
        if (until) return out;
        throw new Error(`Token inesperado: ${t.type}`);
      }
      i++;
      if (t.type === 'if') {
        const then = block(true);
        let otherwise = [];
        if (tokens[i]?.type === 'else') { i++; otherwise = block(true); }
        if (tokens[i]?.type !== 'end' || tokens[i].value !== 'if') throw new Error('Bloco #if não fechado');
        i++;
        out.push({ type: 'if', cond: t.value, then, otherwise });
      } else if (t.type === 'each') {
        const body = block(true);
        if (tokens[i]?.type !== 'end' || tokens[i].value !== 'each') throw new Error('Bloco #each não fechado');
        i++;
        out.push({ type: 'each', expr: t.value, body });
      } else out.push(t);
    }
    if (until) throw new Error('Bloco não fechado');
    return out;
  }
  return block(false);
}

function lookup(path, scopes) {
  if (path === '.') return scopes[0].this;
  const [head, ...rest] = path.split('.');
  let base;
  if (head === 'this') base = scopes[0].this;
  else {
    const s = scopes.find((sc) => sc.vars && head in sc.vars);
    base = s ? s.vars[head] : undefined;
    if (!s) {
      const ctx = scopes.find((sc) => sc.this != null && typeof sc.this === 'object' && head in sc.this);
      base = ctx?.this[head];
    }
  }
  for (const k of rest) base = base == null ? undefined : base[k];
  return base;
}

function run(nodes, scopes) {
  let out = '';
  for (const n of nodes) {
    if (n.type === 'text') out += n.value;
    else if (n.type === 'var') out += esc(lookup(n.value, scopes));
    else if (n.type === 'raw') out += String(lookup(n.value, scopes) ?? '');
    else if (n.type === 'if') {
      const v = lookup(n.cond, scopes);
      out += run(Array.isArray(v) ? (v.length ? n.then : n.otherwise) : v ? n.then : n.otherwise, scopes);
    } else if (n.type === 'each') {
      const m = /^(.+?)(?:\s+as\s+(\w+))?$/.exec(n.expr);
      const list = lookup(m[1].trim(), scopes) ?? [];
      list.forEach((item, index) => {
        const vars = { index };
        if (m[2]) vars[m[2]] = item;
        out += run(n.body, [{ this: item, vars }, ...scopes]);
      });
    }
  }
  return out;
}

export function compile(src) {
  const ast = parse(tokenize(src));
  return (data = {}) => run(ast, [{ this: data, vars: {} }]);
}
