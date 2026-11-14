// Diff de textos linha a linha usando a maior subsequência comum (LCS).

export function lcs(a, b) {
  const tabela = Array.from({ length: a.length + 1 }, () => new Array(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      tabela[i][j] = a[i] === b[j] ? tabela[i + 1][j + 1] + 1 : Math.max(tabela[i + 1][j], tabela[i][j + 1]);
    }
  }
  return tabela;
}

// Retorna operações: { tipo: 'igual' | 'removido' | 'adicionado', linha }
export function diff(antes, depois) {
  const a = antes === '' ? [] : antes.split('\n');
  const b = depois === '' ? [] : depois.split('\n');
  const t = lcs(a, b);
  const ops = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) { ops.push({ tipo: 'igual', linha: a[i] }); i++; j++; }
    else if (t[i + 1][j] >= t[i][j + 1]) ops.push({ tipo: 'removido', linha: a[i++] });
    else ops.push({ tipo: 'adicionado', linha: b[j++] });
  }
  while (i < a.length) ops.push({ tipo: 'removido', linha: a[i++] });
  while (j < b.length) ops.push({ tipo: 'adicionado', linha: b[j++] });
  return ops;
}

export function formatarDiff(ops) {
  const marca = { igual: '  ', removido: '- ', adicionado: '+ ' };
  return ops.map((o) => marca[o.tipo] + o.linha).join('\n');
}

// Reconstrói o texto novo (ou o antigo) a partir das operações.
export function aplicarDiff(ops, direcao = 'depois') {
  const excluir = direcao === 'depois' ? 'removido' : 'adicionado';
  return ops.filter((o) => o.tipo !== excluir).map((o) => o.linha).join('\n');
}

export function estatisticas(ops) {
  const cont = (tipo) => ops.filter((o) => o.tipo === tipo).length;
  return { adicionadas: cont('adicionado'), removidas: cont('removido'), iguais: cont('igual') };
}

export function similaridade(antes, depois) {
  const ops = diff(antes, depois);
  if (ops.length === 0) return 1;
  return (2 * estatisticas(ops).iguais) / (estatisticas(ops).iguais * 2 + estatisticas(ops).adicionadas + estatisticas(ops).removidas);
}
