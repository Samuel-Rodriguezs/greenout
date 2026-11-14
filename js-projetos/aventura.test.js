import test from 'node:test';
import assert from 'node:assert/strict';
import { Aventura } from './aventura.js';

const mapa = () => ({
  hall: { descricao: 'Um hall.', saidas: { norte: 'cofre', leste: 'sala' }, trancadas: { norte: 'chave' } },
  sala: { descricao: 'Uma sala.', saidas: { oeste: 'hall' }, itens: ['chave', 'lanterna'] },
  cofre: { descricao: 'O cofre!', saidas: { sul: 'hall' } },
});

test('descreve sala com itens e saídas', () => {
  const j = new Aventura(mapa(), 'sala');
  assert.equal(j.descrever(), 'Uma sala. Você vê: chave, lanterna. Saídas: oeste.');
});

test('porta trancada exige a chave', () => {
  const j = new Aventura(mapa(), 'hall');
  assert.match(j.executar('ir norte'), /trancada/);
  assert.equal(j.sala, 'hall');
  j.executar('ir leste');
  assert.equal(j.executar('pegar chave'), 'Você pegou chave.');
  j.executar('ir oeste');
  j.executar('ir norte');
  assert.equal(j.sala, 'cofre');
  assert.equal(j.venceu('cofre'), true);
  assert.equal(j.movimentos, 3);
});

test('porta destrancada continua aberta mesmo sem a chave', () => {
  const j = new Aventura(mapa(), 'sala');
  j.executar('pegar chave');
  j.executar('ir oeste');
  j.executar('ir norte');
  j.executar('ir sul');
  j.executar('largar chave');
  assert.match(j.executar('ir norte'), /O cofre/);
});

test('pegar, largar e inventário', () => {
  const j = new Aventura(mapa(), 'sala');
  assert.equal(j.executar('inventario'), 'Você não carrega nada.');
  j.executar('pegar lanterna');
  assert.deepEqual(j.inventario, ['lanterna']);
  assert.equal(j.executar('pegar lanterna'), 'Não há lanterna aqui.');
  j.executar('largar lanterna');
  assert.equal(j.executar('largar lanterna'), 'Você não possui lanterna.');
  assert.match(j.descrever(), /lanterna/);
});

test('comandos inválidos e incompletos', () => {
  const j = new Aventura(mapa(), 'sala');
  assert.equal(j.executar('dançar'), "Não entendi 'dançar'.");
  assert.equal(j.executar('ir'), 'Ir para onde?');
  assert.equal(j.executar('ir sul'), 'Você não pode ir para sul.');
  assert.equal(j.executar('  OLHAR  '), j.descrever());
});

test('valida o mapa', () => {
  assert.throws(() => new Aventura(mapa(), 'x'), /inexistente/);
  assert.throws(() => new Aventura({ a: { descricao: '', saidas: { n: 'b' } } }, 'a'), /não existe/);
});
