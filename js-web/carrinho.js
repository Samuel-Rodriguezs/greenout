// Valores monetários em centavos (inteiros) para evitar erros de ponto flutuante.
export function createCarrinho({ cupons = {}, frete = () => 0 } = {}) {
  const itens = new Map(); // sku -> { sku, nome, preco, qtd }
  const aplicados = [];

  const subtotalItens = () => [...itens.values()].reduce((s, i) => s + i.preco * i.qtd, 0);

  function calcularDesconto(cupom, base) {
    if (cupom.minimo && base < cupom.minimo) return 0;
    let d = cupom.tipo === 'percentual' ? Math.round((base * cupom.valor) / 100) : cupom.valor;
    if (cupom.max) d = Math.min(d, cupom.max);
    return Math.min(d, base);
  }

  function totais() {
    const subtotal = subtotalItens();
    let restante = subtotal;
    const descontos = [];
    for (const codigo of aplicados) {
      const d = calcularDesconto(cupons[codigo], restante);
      descontos.push({ codigo, valor: d });
      restante -= d;
    }
    const desconto = subtotal - restante;
    const f = restante > 0 ? frete({ subtotal, itens: [...itens.values()], total: restante }) : 0;
    return { subtotal, descontos, desconto, frete: f, total: restante + f };
  }

  return {
    adicionar(item, qtd = 1) {
      if (!Number.isInteger(item.preco) || item.preco < 0) throw new Error('preco deve ser inteiro em centavos');
      if (!Number.isInteger(qtd) || qtd < 1) throw new Error('quantidade inválida');
      const atual = itens.get(item.sku);
      if (atual) atual.qtd += qtd;
      else itens.set(item.sku, { sku: item.sku, nome: item.nome, preco: item.preco, qtd });
    },
    alterarQtd(sku, qtd) {
      if (!itens.has(sku)) throw new Error(`Item inexistente: ${sku}`);
      if (qtd <= 0) itens.delete(sku);
      else itens.get(sku).qtd = qtd;
    },
    remover(sku) { itens.delete(sku); },
    aplicarCupom(codigo) {
      const c = cupons[codigo.toUpperCase()];
      const cod = codigo.toUpperCase();
      if (!c) throw new Error('Cupom inválido');
      if (aplicados.includes(cod)) throw new Error('Cupom já aplicado');
      if (c.expira && new Date(c.expira) < new Date(c.agora ?? Date.now())) throw new Error('Cupom expirado');
      if (aplicados.some((a) => !cupons[a].cumulativo) || (aplicados.length && !c.cumulativo)) {
        throw new Error('Cupom não cumulativo');
      }
      if (c.minimo && subtotalItens() < c.minimo) throw new Error('Valor mínimo não atingido');
      aplicados.push(cod);
    },
    removerCupom(codigo) {
      const i = aplicados.indexOf(codigo.toUpperCase());
      if (i >= 0) aplicados.splice(i, 1);
    },
    totais,
    itens: () => [...itens.values()].map((i) => ({ ...i })),
    get quantidade() { return [...itens.values()].reduce((s, i) => s + i.qtd, 0); },
    get cupons() { return [...aplicados]; },
    vazio: () => itens.size === 0,
  };
}
