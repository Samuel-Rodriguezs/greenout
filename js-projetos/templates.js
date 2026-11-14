// Motor de templates: {{var}}, caminhos {{a.b}}, filtros {{nome | maiuscula}},
// escape HTML por padrão ({{{var}}} para bruto), {{#se x}}...{{/se}} e {{#cada xs}}...{{/cada}}.

const FILTROS = {
  maiuscula: (v) => String(v).toUpperCase(),
  minuscula: (v) => String(v).toLowerCase(),
  moeda: (v) => `R$ ${Number(v).toFixed(2).replace('.', ',')}`,
  json: (v) => JSON.stringify(v),
};

const escapar = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

function resolver(caminho, contexto) {
  if (caminho === '.') return contexto.item;
  let atual = contexto;
  for (const parte of caminho.split('.')) {
    if (atual === null || atual === undefined) return undefined;
    atual = atual[parte];
  }
  return atual;
}

function valorComFiltros(expr, contexto) {
  const [caminho, ...filtros] = expr.split('|').map((s) => s.trim());
  let v = resolver(caminho, contexto);
  for (const nome of filtros) {
    if (!FILTROS[nome]) throw new Error(`Filtro desconhecido: ${nome}`);
    v = FILTROS[nome](v);
  }
  return v;
}

export function renderizar(template, dados = {}, contexto = { ...dados }) {
  // Blocos primeiro (não aninhados do mesmo tipo), depois variáveis.
  let saida = template.replace(/\{\{#(se|cada)\s+([^}]+?)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (_, tipo, expr, corpo) => {
    const v = resolver(expr.trim(), contexto);
    if (tipo === 'se') return v && !(Array.isArray(v) && v.length === 0) ? renderizar(corpo, dados, contexto) : '';
    if (!Array.isArray(v)) return '';
    return v
      .map((item, i) =>
        renderizar(corpo, dados, { ...contexto, ...(typeof item === 'object' && item ? item : {}), item, indice: i }),
      )
      .join('');
  });
  if (/\{\{#(se|cada)\b/.test(saida) && !/\{\{\/(se|cada)\}\}/.test(saida)) {
    throw new Error('Bloco não fechado');
  }
  saida = saida.replace(/\{\{\{\s*([^}]+?)\s*\}\}\}/g, (_, e) => String(valorComFiltros(e, contexto) ?? ''));
  return saida.replace(/\{\{\s*([^#/}][^}]*?)\s*\}\}/g, (_, e) => escapar(valorComFiltros(e, contexto) ?? ''));
}
