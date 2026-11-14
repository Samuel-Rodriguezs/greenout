// Interpolação polinomial de Lagrange e diferenças divididas de Newton.

function validar(pontos) {
  if (pontos.length === 0) throw new RangeError('é preciso ao menos um ponto');
  const xs = new Set(pontos.map(([x]) => x));
  if (xs.size !== pontos.length) throw new RangeError('abscissas repetidas');
}

// Avalia o polinômio interpolador em x. pontos = [[x0,y0],...].
export function lagrange(pontos, x) {
  validar(pontos);
  let soma = 0;
  for (let i = 0; i < pontos.length; i++) {
    let termo = pontos[i][1];
    for (let j = 0; j < pontos.length; j++) {
      if (i !== j) termo *= (x - pontos[j][0]) / (pontos[i][0] - pontos[j][0]);
    }
    soma += termo;
  }
  return soma;
}

// Coeficientes do polinômio interpolador (menor grau primeiro).
export function coeficientes(pontos) {
  validar(pontos);
  const n = pontos.length;
  let resultado = new Array(n).fill(0);
  for (let i = 0; i < n; i++) {
    // base de Lagrange li(x) como polinômio
    let base = [1];
    let denom = 1;
    for (let j = 0; j < n; j++) {
      if (i === j) continue;
      const nova = new Array(base.length + 1).fill(0);
      base.forEach((c, k) => { nova[k + 1] += c; nova[k] -= c * pontos[j][0]; });
      base = nova;
      denom *= pontos[i][0] - pontos[j][0];
    }
    base.forEach((c, k) => { resultado[k] += (pontos[i][1] * c) / denom; });
  }
  return resultado.map((c) => (Math.abs(c) < 1e-12 ? 0 : c));
}

// Avalia polinômio (menor grau primeiro) por Horner.
export function horner(coefs, x) {
  return coefs.reduceRight((acc, c) => acc * x + c, 0);
}

// Diferenças divididas de Newton: devolve função avaliadora.
export function newton(pontos) {
  validar(pontos);
  const n = pontos.length;
  const xs = pontos.map(([x]) => x);
  const dd = pontos.map(([, y]) => y);
  for (let nivel = 1; nivel < n; nivel++) {
    for (let i = n - 1; i >= nivel; i--) dd[i] = (dd[i] - dd[i - 1]) / (xs[i] - xs[i - nivel]);
  }
  return (x) => {
    let r = dd[n - 1];
    for (let i = n - 2; i >= 0; i--) r = r * (x - xs[i]) + dd[i];
    return r;
  };
}
