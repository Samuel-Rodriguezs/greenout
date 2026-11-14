// Matrizes de transformação homogêneas: 3x3 (2D) e 4x4 (3D).
// Armazenadas em array plano, linha por linha; vetores-coluna (M * v).

class Matriz {
  constructor(n, dados) {
    if (dados.length !== n * n) throw new RangeError(`esperado ${n * n} elementos`);
    this.n = n;
    this.m = Object.freeze([...dados]);
    Object.freeze(this);
  }

  /** this * outra: aplica `outra` primeiro, depois `this`. */
  multiplica(outra) {
    const { n } = this;
    if (outra.n !== n) throw new RangeError('dimensões incompatíveis');
    const r = new Array(n * n).fill(0);
    for (let i = 0; i < n; i++)
      for (let j = 0; j < n; j++)
        for (let k = 0; k < n; k++) r[i * n + j] += this.m[i * n + k] * outra.m[k * n + j];
    return new this.constructor(r);
  }

  transposta() {
    const { n } = this;
    const r = [];
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) r.push(this.m[j * n + i]);
    return new this.constructor(r);
  }

  /** Inversa por Gauss-Jordan com pivoteamento parcial. */
  inversa() {
    const { n } = this;
    const a = [];
    for (let i = 0; i < n; i++) {
      a.push([...this.m.slice(i * n, i * n + n), ...Array.from({ length: n }, (_, j) => (i === j ? 1 : 0))]);
    }
    for (let c = 0; c < n; c++) {
      let p = c;
      for (let i = c + 1; i < n; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
      if (Math.abs(a[p][c]) < 1e-12) throw new RangeError('matriz singular');
      [a[c], a[p]] = [a[p], a[c]];
      const piv = a[c][c];
      for (let j = 0; j < 2 * n; j++) a[c][j] /= piv;
      for (let i = 0; i < n; i++) {
        if (i === c) continue;
        const f = a[i][c];
        if (f !== 0) for (let j = 0; j < 2 * n; j++) a[i][j] -= f * a[c][j];
      }
    }
    return new this.constructor(a.flatMap((l) => l.slice(n)));
  }

  determinante() {
    const { n } = this;
    const a = Array.from({ length: n }, (_, i) => this.m.slice(i * n, i * n + n));
    let det = 1;
    for (let c = 0; c < n; c++) {
      let p = c;
      for (let i = c + 1; i < n; i++) if (Math.abs(a[i][c]) > Math.abs(a[p][c])) p = i;
      if (a[p][c] === 0) return 0;
      if (p !== c) { [a[c], a[p]] = [a[p], a[c]]; det = -det; }
      det *= a[c][c];
      for (let i = c + 1; i < n; i++) {
        const f = a[i][c] / a[c][c];
        for (let j = c; j < n; j++) a[i][j] -= f * a[c][j];
      }
    }
    return det;
  }
}

export class Mat3 extends Matriz {
  constructor(dados) { super(3, dados); }
  static identidade() { return new Mat3([1, 0, 0, 0, 1, 0, 0, 0, 1]); }
  static translacao(tx, ty) { return new Mat3([1, 0, tx, 0, 1, ty, 0, 0, 1]); }
  static escala(sx, sy = sx) { return new Mat3([sx, 0, 0, 0, sy, 0, 0, 0, 1]); }
  static rotacao(rad) {
    const c = Math.cos(rad), s = Math.sin(rad);
    return new Mat3([c, -s, 0, s, c, 0, 0, 0, 1]);
  }
  /** Rotação em torno de um ponto qualquer. */
  static rotacaoEm(rad, cx, cy) {
    return Mat3.translacao(cx, cy).multiplica(Mat3.rotacao(rad)).multiplica(Mat3.translacao(-cx, -cy));
  }
  static reflexaoX() { return Mat3.escala(1, -1); }
  static cisalhamento(kx, ky = 0) { return new Mat3([1, kx, 0, ky, 1, 0, 0, 0, 1]); }
  aplica([x, y]) {
    const m = this.m;
    const w = m[6] * x + m[7] * y + m[8];
    return [(m[0] * x + m[1] * y + m[2]) / w, (m[3] * x + m[4] * y + m[5]) / w];
  }
}

export class Mat4 extends Matriz {
  constructor(dados) { super(4, dados); }
  static identidade() { return new Mat4([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]); }
  static translacao(tx, ty, tz) { return new Mat4([1, 0, 0, tx, 0, 1, 0, ty, 0, 0, 1, tz, 0, 0, 0, 1]); }
  static escala(sx, sy = sx, sz = sx) { return new Mat4([sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, 0, 0, 0, 1]); }
  static rotacaoX(r) {
    const c = Math.cos(r), s = Math.sin(r);
    return new Mat4([1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1]);
  }
  static rotacaoY(r) {
    const c = Math.cos(r), s = Math.sin(r);
    return new Mat4([c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1]);
  }
  static rotacaoZ(r) {
    const c = Math.cos(r), s = Math.sin(r);
    return new Mat4([c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  }
  /** Rotação em torno de eixo arbitrário (fórmula de Rodrigues). */
  static rotacaoEixo([ex, ey, ez], r) {
    const l = Math.hypot(ex, ey, ez);
    if (l === 0) throw new RangeError('eixo nulo');
    const [x, y, z] = [ex / l, ey / l, ez / l];
    const c = Math.cos(r), s = Math.sin(r), t = 1 - c;
    return new Mat4([
      t * x * x + c, t * x * y - s * z, t * x * z + s * y, 0,
      t * x * y + s * z, t * y * y + c, t * y * z - s * x, 0,
      t * x * z - s * y, t * y * z + s * x, t * z * z + c, 0,
      0, 0, 0, 1,
    ]);
  }
  aplica([x, y, z]) {
    const m = this.m;
    const w = m[12] * x + m[13] * y + m[14] * z + m[15];
    return [
      (m[0] * x + m[1] * y + m[2] * z + m[3]) / w,
      (m[4] * x + m[5] * y + m[6] * z + m[7]) / w,
      (m[8] * x + m[9] * y + m[10] * z + m[11]) / w,
    ];
  }
}
