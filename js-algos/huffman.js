// Codificação de Huffman. Bits como string de '0'/'1' (didático).
import { FilaPrioridade } from './filaPrioridade.js';

// Constrói a árvore; folhas { simbolo, freq }, nós { esq, dir, freq }.
export function construirArvore(texto) {
  const freq = new Map();
  for (const c of texto) freq.set(c, (freq.get(c) ?? 0) + 1);
  if (freq.size === 0) return null;
  let ordem = 0; // desempate determinístico
  const fila = new FilaPrioridade((a, b) => a.freq - b.freq || a.ordem - b.ordem);
  for (const [simbolo, f] of [...freq].sort((a, b) => (a[0] < b[0] ? -1 : 1))) {
    fila.inserir({ simbolo, freq: f, ordem: ordem++ });
  }
  while (fila.tamanho > 1) {
    const esq = fila.remover(), dir = fila.remover();
    fila.inserir({ esq, dir, freq: esq.freq + dir.freq, ordem: ordem++ });
  }
  return fila.remover();
}

export function tabelaCodigos(arvore) {
  const tabela = new Map();
  if (!arvore) return tabela;
  if (arvore.simbolo !== undefined) { tabela.set(arvore.simbolo, '0'); return tabela; } // um só símbolo
  const andar = (no, prefixo) => {
    if (no.simbolo !== undefined) { tabela.set(no.simbolo, prefixo); return; }
    andar(no.esq, prefixo + '0');
    andar(no.dir, prefixo + '1');
  };
  andar(arvore, '');
  return tabela;
}

export function codificar(texto) {
  const arvore = construirArvore(texto);
  const tabela = tabelaCodigos(arvore);
  let bits = '';
  for (const c of texto) bits += tabela.get(c);
  return { bits, arvore };
}

export function decodificar(bits, arvore) {
  if (!arvore) return '';
  if (arvore.simbolo !== undefined) return arvore.simbolo.repeat(bits.length);
  let saida = '', no = arvore;
  for (const b of bits) {
    if (b !== '0' && b !== '1') throw new SyntaxError(`bit inválido: ${b}`);
    no = b === '0' ? no.esq : no.dir;
    if (no.simbolo !== undefined) { saida += no.simbolo; no = arvore; }
  }
  if (no !== arvore) throw new SyntaxError('sequência de bits truncada');
  return saida;
}
