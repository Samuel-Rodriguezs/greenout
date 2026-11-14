export function h(tag, props = {}, ...children) {
  return { tag, props: props ?? {}, children: children.flat().map((c) => (typeof c === 'object' && c !== null ? c : String(c))) };
}

const isText = (n) => typeof n === 'string';

export function create(node, path = []) {
  return [{ op: 'CREATE', path, node }];
}

function diffProps(oldP, newP, path) {
  const ops = [];
  for (const k of Object.keys(oldP)) {
    if (!(k in newP)) ops.push({ op: 'REMOVE_PROP', path, name: k });
  }
  for (const [k, v] of Object.entries(newP)) {
    if (oldP[k] !== v) ops.push({ op: 'SET_PROP', path, name: k, value: v });
  }
  return ops;
}

function diffChildren(oldC, newC, path) {
  const ops = [];
  const hasKeys = newC.some((c) => !isText(c) && c.props?.key != null);
  if (!hasKeys) {
    const n = Math.max(oldC.length, newC.length);
    for (let i = 0; i < n; i++) ops.push(...patch(oldC[i], newC[i], [...path, i]));
    return ops;
  }
  const keyOf = (c) => (isText(c) ? undefined : c.props?.key);
  const oldByKey = new Map();
  oldC.forEach((c, i) => { if (keyOf(c) != null) oldByKey.set(keyOf(c), { c, i }); });
  const used = new Set();
  newC.forEach((c, i) => {
    const k = keyOf(c);
    const old = k != null ? oldByKey.get(k) : undefined;
    if (old) {
      used.add(k);
      ops.push(...patch(old.c, c, [...path, old.i]));
      if (old.i !== i) ops.push({ op: 'MOVE', path, key: k, from: old.i, to: i });
    } else {
      ops.push({ op: 'INSERT', path, index: i, node: c });
    }
  });
  for (const [k, { i }] of oldByKey) {
    if (!used.has(k)) ops.push({ op: 'REMOVE', path: [...path, i] });
  }
  return ops;
}

export function patch(oldNode, newNode, path = []) {
  if (oldNode === undefined && newNode === undefined) return [];
  if (oldNode === undefined) return [{ op: 'CREATE', path, node: newNode }];
  if (newNode === undefined) return [{ op: 'REMOVE', path }];
  if (isText(oldNode) || isText(newNode)) {
    if (oldNode === newNode) return [];
    return [{ op: 'REPLACE', path, node: newNode }];
  }
  if (oldNode.tag !== newNode.tag) return [{ op: 'REPLACE', path, node: newNode }];
  return [
    ...diffProps(oldNode.props, newNode.props, path),
    ...diffChildren(oldNode.children, newNode.children, path),
  ];
}

export function render(node) {
  if (isText(node)) return escapeHtml(node);
  const attrs = Object.entries(node.props)
    .filter(([k, v]) => k !== 'key' && v !== false && v != null)
    .map(([k, v]) => (v === true ? ` ${k}` : ` ${k}="${escapeHtml(String(v))}"`))
    .join('');
  return `<${node.tag}${attrs}>${node.children.map(render).join('')}</${node.tag}>`;
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
