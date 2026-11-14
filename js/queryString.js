// Parser e serializador de query string (chaves repetidas viram arrays).

function decodificar(texto) {
  const t = texto.replace(/\+/g, ' ');
  try {
    return decodeURIComponent(t);
  } catch {
    return t; // sequência % malformada: mantém o texto original
  }
}

export function parseQuery(entrada) {
  let texto = String(entrada ?? '');
  const interrogacao = texto.indexOf('?');
  if (interrogacao !== -1) texto = texto.slice(interrogacao + 1);
  const hash = texto.indexOf('#');
  if (hash !== -1) texto = texto.slice(0, hash);

  const resultado = Object.create(null);
  for (const parte of texto.split('&')) {
    if (parte === '') continue;
    const igual = parte.indexOf('=');
    const chave = decodificar(igual === -1 ? parte : parte.slice(0, igual));
    const valor = igual === -1 ? '' : decodificar(parte.slice(igual + 1));
    if (chave in resultado) {
      resultado[chave] = [].concat(resultado[chave], valor);
    } else {
      resultado[chave] = valor;
    }
  }
  return { ...resultado };
}

export function stringifyQuery(objeto) {
  const partes = [];
  for (const [chave, valor] of Object.entries(objeto)) {
    const valores = Array.isArray(valor) ? valor : [valor];
    for (const v of valores) {
      if (v === undefined || v === null) continue;
      partes.push(`${encodeURIComponent(chave)}=${encodeURIComponent(v)}`);
    }
  }
  return partes.join('&');
}
