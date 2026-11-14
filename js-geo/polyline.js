// Encoded Polyline Algorithm Format (Google). Pontos são [lat, lon].

function codificaValor(v) {
  let n = v < 0 ? ~(v << 1) : v << 1;
  let s = '';
  while (n >= 0x20) {
    s += String.fromCharCode((0x20 | (n & 0x1f)) + 63);
    n >>= 5;
  }
  return s + String.fromCharCode(n + 63);
}

export function codifica(pontos, precisao = 5) {
  const f = 10 ** precisao;
  let anteriorLat = 0, anteriorLon = 0, saida = '';
  for (const [lat, lon] of pontos) {
    const la = Math.round(lat * f), lo = Math.round(lon * f);
    saida += codificaValor(la - anteriorLat) + codificaValor(lo - anteriorLon);
    anteriorLat = la;
    anteriorLon = lo;
  }
  return saida;
}

export function decodifica(texto, precisao = 5) {
  const f = 10 ** precisao;
  const pontos = [];
  let i = 0, lat = 0, lon = 0;
  const le = () => {
    let resultado = 0, shift = 0, byte;
    do {
      if (i >= texto.length) throw new RangeError('polyline truncada');
      byte = texto.charCodeAt(i++) - 63;
      if (byte < 0 || byte > 63) throw new RangeError(`caractere inválido na posição ${i - 1}`);
      resultado |= (byte & 0x1f) << shift;
      shift += 5;
    } while (byte >= 0x20);
    return resultado & 1 ? ~(resultado >> 1) : resultado >> 1;
  };
  while (i < texto.length) {
    lat += le();
    lon += le();
    pontos.push([lat / f, lon / f]);
  }
  return pontos;
}
