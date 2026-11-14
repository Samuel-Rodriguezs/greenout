import test from 'node:test';
import assert from 'node:assert/strict';
import { sortRows, toggleSort, paginate, pageNumbers, tableView } from './tabela.js';

const rows = [
  { n: 'Bruno', idade: 30 },
  { n: 'ana', idade: 25 },
  { n: 'Álvaro', idade: 30 },
  { n: 'Carla', idade: null },
];

test('ordena texto com locale pt-BR', () => {
  assert.deepEqual(sortRows(rows, [{ key: 'n' }]).map((r) => r.n), ['Álvaro', 'ana', 'Bruno', 'Carla']);
});

test('desc e nulos sempre por último no asc', () => {
  assert.deepEqual(sortRows(rows, [{ key: 'idade' }]).map((r) => r.n), ['ana', 'Bruno', 'Álvaro', 'Carla']);
  assert.equal(sortRows(rows, [{ key: 'idade', dir: 'desc' }])[0].n, 'Carla');
});

test('multi-coluna e estabilidade', () => {
  const r = sortRows(rows, [{ key: 'idade', dir: 'desc' }, { key: 'n' }]);
  assert.deepEqual(r.map((x) => x.n).slice(0, 3), ['Carla', 'Álvaro', 'Bruno']);
  assert.deepEqual(sortRows(rows, []).map((x) => x.n), rows.map((x) => x.n));
});

test('números naturais', () => {
  const r = sortRows([{ f: 'a10' }, { f: 'a2' }], [{ key: 'f' }]);
  assert.equal(r[0].f, 'a2');
});

test('toggleSort cicla asc -> desc -> nenhum', () => {
  let s = toggleSort([], 'n');
  assert.deepEqual(s, [{ key: 'n', dir: 'asc' }]);
  s = toggleSort(s, 'n');
  assert.equal(s[0].dir, 'desc');
  assert.deepEqual(toggleSort(s, 'n'), []);
});

test('paginate', () => {
  const data = Array.from({ length: 25 }, (_, i) => i);
  const p = paginate(data, 3, 10);
  assert.deepEqual(p.rows, [20, 21, 22, 23, 24]);
  assert.deepEqual([p.totalPages, p.hasNext, p.hasPrev], [3, false, true]);
  assert.equal(paginate(data, 99, 10).page, 3);
  assert.equal(paginate([], 1, 10).totalPages, 1);
  assert.throws(() => paginate(data, 1, 0));
});

test('pageNumbers com reticências', () => {
  assert.deepEqual(pageNumbers(1, 5), [1, 2, 3, 4, 5].slice(0, 2).concat([ '…', 5 ]));
  assert.deepEqual(pageNumbers(5, 10), [1, '…', 4, 5, 6, '…', 10]);
  assert.deepEqual(pageNumbers(3, 5), [1, 2, 3, 4, 5]);
});

test('tableView combina filtro, ordem e página', () => {
  const v = tableView(rows, { filter: (r) => r.idade === 30, sorts: [{ key: 'n' }], pageSize: 1, page: 2 });
  assert.equal(v.total, 2);
  assert.equal(v.rows[0].n, 'Bruno');
});
