import test from 'node:test';
import assert from 'node:assert/strict';
import { h, create, patch, render } from './vdom.js';

test('h normaliza filhos', () => {
  const n = h('ul', {}, [h('li', {}, 1), h('li', {}, 2)]);
  assert.equal(n.children.length, 2);
  assert.equal(h('p', null, 5).children[0], '5');
});

test('create gera operação', () => {
  const n = h('div');
  assert.deepEqual(create(n), [{ op: 'CREATE', path: [], node: n }]);
});

test('árvores iguais não geram ops', () => {
  const a = h('div', { id: 'x' }, h('span', {}, 'oi'));
  const b = h('div', { id: 'x' }, h('span', {}, 'oi'));
  assert.deepEqual(patch(a, b), []);
});

test('props alteradas e removidas', () => {
  const ops = patch(h('div', { a: 1, b: 2 }), h('div', { a: 1, b: 3, c: 4 }));
  assert.deepEqual(ops, [
    { op: 'SET_PROP', path: [], name: 'b', value: 3 },
    { op: 'SET_PROP', path: [], name: 'c', value: 4 },
  ]);
  assert.deepEqual(patch(h('div', { a: 1 }), h('div', {})), [{ op: 'REMOVE_PROP', path: [], name: 'a' }]);
});

test('troca de tag substitui', () => {
  const n = h('p');
  assert.deepEqual(patch(h('div'), n), [{ op: 'REPLACE', path: [], node: n }]);
});

test('texto alterado', () => {
  const ops = patch(h('p', {}, 'a'), h('p', {}, 'b'));
  assert.deepEqual(ops, [{ op: 'REPLACE', path: [0], node: 'b' }]);
});

test('filhos adicionados e removidos', () => {
  const li = h('li', {}, 'c');
  assert.deepEqual(patch(h('ul', {}, h('li', {}, 'a')), h('ul', {}, h('li', {}, 'a'), li)), [
    { op: 'CREATE', path: [1], node: li },
  ]);
  assert.deepEqual(patch(h('ul', {}, h('li'), h('li')), h('ul', {}, h('li'))), [{ op: 'REMOVE', path: [1] }]);
});

test('listas com key: move, insere e remove', () => {
  const item = (k) => h('li', { key: k }, k);
  const ops = patch(h('ul', {}, item('a'), item('b'), item('c')), h('ul', {}, item('c'), item('a'), item('d')));
  assert.deepEqual(ops.map((o) => o.op), ['MOVE', 'MOVE', 'INSERT', 'REMOVE']);
  assert.deepEqual(ops[0], { op: 'MOVE', path: [], key: 'c', from: 2, to: 0 });
  assert.deepEqual(ops[3], { op: 'REMOVE', path: [1] });
});

test('render escapa HTML', () => {
  assert.equal(render(h('p', { class: 'a"b', hidden: true, key: 'k' }, '<x>')), '<p class="a&quot;b" hidden>&lt;x&gt;</p>');
});
