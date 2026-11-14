// Store estilo Redux: estado único, reducer puro, subscribe e middlewares.

export function criarStore(reducer, estadoInicial, ...middlewares) {
  if (typeof reducer !== 'function') throw new TypeError('reducer deve ser uma função');
  let estado = estadoInicial;
  let ouvintes = [];
  let despachando = false;

  const getState = () => estado;

  function subscribe(fn) {
    if (typeof fn !== 'function') throw new TypeError('ouvinte deve ser uma função');
    ouvintes.push(fn);
    let ativo = true;
    return () => {
      if (!ativo) return;
      ativo = false;
      ouvintes = ouvintes.filter((o) => o !== fn);
    };
  }

  function despachoBase(acao) {
    if (!acao || typeof acao.tipo !== 'string') throw new TypeError('Ação precisa ter "tipo" string');
    if (despachando) throw new Error('Reducers não podem despachar ações');
    try {
      despachando = true;
      estado = reducer(estado, acao);
    } finally {
      despachando = false;
    }
    for (const fn of [...ouvintes]) fn();
    return acao;
  }

  let dispatch = despachoBase;
  const api = { getState, dispatch: (a) => dispatch(a) };
  // Middleware: (api) => (proximo) => (acao) => ...
  for (const mw of [...middlewares].reverse()) dispatch = mw(api)(dispatch);

  despachoBase({ tipo: '@@INIT' });
  return { getState, subscribe, dispatch: (a) => dispatch(a) };
}

export function combinarReducers(mapa) {
  return (estado = {}, acao) => {
    let mudou = false;
    const novo = {};
    for (const [chave, red] of Object.entries(mapa)) {
      novo[chave] = red(estado[chave], acao);
      if (novo[chave] !== estado[chave]) mudou = true;
    }
    return mudou ? novo : estado;
  };
}

export const loggerMiddleware = (log) => (api) => (proximo) => (acao) => {
  const antes = api.getState();
  const r = proximo(acao);
  log({ acao, antes, depois: api.getState() });
  return r;
};
