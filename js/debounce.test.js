import { test } from 'node:test';
import assert from 'node:assert/strict';
import { debounce, throttle } from './debounce.js';

// Relógio falso mínimo.
function criarRelogio() {
  let agora = 0;
  let proximoId = 1;
  const tarefas = new Map();
  return {
    setTimeout(fn, ms) {
      const id = proximoId++;
      tarefas.set(id, { fn, quando: agora + ms });
      return id;
    },
    clearTimeout(id) {
      tarefas.delete(id);
    },
    avancar(ms) {
      const alvo = agora + ms;
      for (;;) {
        const prontas = [...tarefas.entries()]
          .filter(([, t]) => t.quando <= alvo)
          .sort((a, b) => a[1].quando - b[1].quando);
        if (prontas.length === 0) break;
        const [id, t] = prontas[0];
        tarefas.delete(id);
        agora = t.quando;
        t.fn();
      }
      agora = alvo;
    },
  };
}

test('debounce só dispara após silêncio, com últimos argumentos', () => {
  const relogio = criarRelogio();
  const chamadas = [];
  const d = debounce((x) => chamadas.push(x), 100, relogio);
  d(1);
  relogio.avancar(50);
  d(2);
  relogio.avancar(99);
  assert.deepEqual(chamadas, []);
  relogio.avancar(1);
  assert.deepEqual(chamadas, [2]);
});

test('debounce.cancelar impede a execução', () => {
  const relogio = criarRelogio();
  let n = 0;
  const d = debounce(() => n++, 10, relogio);
  d();
  d.cancelar();
  relogio.avancar(100);
  assert.equal(n, 0);
});

test('debounce preserva this', () => {
  const relogio = criarRelogio();
  const obj = { v: 7, f: debounce(function () { this.visto = this.v; }, 5, relogio) };
  obj.f();
  relogio.avancar(5);
  assert.equal(obj.visto, 7);
});

test('throttle executa imediatamente e depois uma vez no final', () => {
  const relogio = criarRelogio();
  const chamadas = [];
  const t = throttle((x) => chamadas.push(x), 100, relogio);
  t('a');
  t('b');
  t('c');
  assert.deepEqual(chamadas, ['a']);
  relogio.avancar(100);
  assert.deepEqual(chamadas, ['a', 'c']);
  relogio.avancar(100);
  assert.deepEqual(chamadas, ['a', 'c']);
  t('d');
  assert.deepEqual(chamadas, ['a', 'c', 'd']);
});

test('throttle sem chamadas extras não dispara trailing', () => {
  const relogio = criarRelogio();
  let n = 0;
  const t = throttle(() => n++, 50, relogio);
  t();
  relogio.avancar(500);
  assert.equal(n, 1);
});
