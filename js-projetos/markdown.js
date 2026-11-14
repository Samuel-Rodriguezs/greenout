// Conversor simples de Markdown para HTML: títulos, listas, citações,
// blocos de código, parágrafos, negrito, itálico, código inline e links.

export function escaparHtml(texto) {
  return texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function inline(texto) {
  const codigos = [];
  let s = escaparHtml(texto).replace(/`([^`]+)`/g, (_, c) => {
    codigos.push(`<code>${c}</code>`);
    return `\u0000${codigos.length - 1}\u0000`;
  });
  s = s
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => codigos[Number(i)]);
}

export function markdownParaHtml(md) {
  const linhas = md.replace(/\r\n/g, '\n').split('\n');
  const saida = [];
  let i = 0;

  const ehEspecial = (l) => /^(#{1,6}\s|[-*]\s|\d+\.\s|>\s?|```)/.test(l);

  while (i < linhas.length) {
    const linha = linhas[i];

    if (linha.trim() === '') { i++; continue; }

    if (linha.startsWith('```')) {
      const codigo = [];
      i++;
      while (i < linhas.length && !linhas[i].startsWith('```')) codigo.push(linhas[i++]);
      if (i >= linhas.length) throw new Error('Bloco de código não fechado');
      i++;
      saida.push(`<pre><code>${escaparHtml(codigo.join('\n'))}</code></pre>`);
      continue;
    }

    const titulo = /^(#{1,6})\s+(.*)$/.exec(linha);
    if (titulo) {
      const n = titulo[1].length;
      saida.push(`<h${n}>${inline(titulo[2].trim())}</h${n}>`);
      i++;
      continue;
    }

    const lista = /^([-*]|\d+\.)\s+/.exec(linha);
    if (lista) {
      const ordenada = /\d/.test(lista[1]);
      const re = ordenada ? /^\d+\.\s+(.*)$/ : /^[-*]\s+(.*)$/;
      const itens = [];
      let m;
      while (i < linhas.length && (m = re.exec(linhas[i]))) {
        itens.push(`<li>${inline(m[1])}</li>`);
        i++;
      }
      const tag = ordenada ? 'ol' : 'ul';
      saida.push(`<${tag}>${itens.join('')}</${tag}>`);
      continue;
    }

    if (/^>\s?/.test(linha)) {
      const partes = [];
      while (i < linhas.length && /^>\s?/.test(linhas[i])) partes.push(linhas[i++].replace(/^>\s?/, ''));
      saida.push(`<blockquote>${markdownParaHtml(partes.join('\n'))}</blockquote>`);
      continue;
    }

    const paragrafo = [];
    while (i < linhas.length && linhas[i].trim() !== '' && !ehEspecial(linhas[i])) paragrafo.push(linhas[i++].trim());
    saida.push(`<p>${inline(paragrafo.join(' '))}</p>`);
  }
  return saida.join('\n');
}
