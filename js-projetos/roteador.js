// Roteador de URLs com parâmetros (/usuarios/:id), curinga (*), query string e métodos HTTP.

function compilar(padrao) {
  const nomes = [];
  const partes = padrao.split('/').filter(Boolean).map((p) => {
    if (p === '*') { nomes.push('*'); return '(.*)'; }
    if (p.startsWith(':')) { nomes.push(p.slice(1)); return '([^/]+)'; }
    return p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  });
  return { regex: new RegExp(`^/${partes.join('/')}/?$`), nomes };
}

export class Roteador {
  #rotas = [];

  adicionar(metodo, padrao, handler) {
    if (!padrao.startsWith('/')) throw new Error('Padrão deve começar com /');
    if (typeof handler !== 'function') throw new TypeError('Handler deve ser função');
    this.#rotas.push({ metodo: metodo.toUpperCase(), padrao, handler, ...compilar(padrao) });
    return this;
  }

  get(padrao, h) { return this.adicionar('GET', padrao, h); }
  post(padrao, h) { return this.adicionar('POST', padrao, h); }

  // Retorna { handler, params, query } ou null.
  resolver(metodo, url) {
    const [caminho, qs = ''] = url.split('?');
    const query = Object.fromEntries(new URLSearchParams(qs));
    for (const r of this.#rotas) {
      if (r.metodo !== metodo.toUpperCase()) continue;
      const m = r.regex.exec(caminho);
      if (!m) continue;
      const params = {};
      r.nomes.forEach((n, i) => { params[n] = decodeURIComponent(m[i + 1]); });
      return { handler: r.handler, params, query, padrao: r.padrao };
    }
    return null;
  }

  // Executa o handler; devolve { status, corpo }.
  despachar(metodo, url) {
    const achou = this.resolver(metodo, url);
    if (achou) return { status: 200, corpo: achou.handler({ params: achou.params, query: achou.query }) };
    const caminho = url.split('?')[0];
    const outroMetodo = this.#rotas.some((r) => r.regex.test(caminho));
    return outroMetodo ? { status: 405, corpo: 'Método não permitido' } : { status: 404, corpo: 'Não encontrado' };
  }
}
