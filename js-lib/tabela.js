// Renderiza uma tabela ASCII a partir de cabeçalhos e linhas. Números alinham à direita.
export function tabela(cabecalhos, linhas) {
  const cel = (v) => String(v ?? '');
  const larg = cabecalhos.map((h, i) => Math.max(cel(h).length, ...linhas.map((l) => cel(l[i]).length)));
  const sep = '+' + larg.map((w) => '-'.repeat(w + 2)).join('+') + '+';
  const fmt = (l) => '|' + larg.map((w, i) => {
    const v = cel(l[i]);
    return ' ' + (typeof l[i] === 'number' ? v.padStart(w) : v.padEnd(w)) + ' ';
  }).join('|') + '|';
  return [sep, fmt(cabecalhos.map(String)), sep, ...linhas.map(fmt), sep].join('\n');
}
