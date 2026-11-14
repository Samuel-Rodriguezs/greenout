// Vetores 2D e 3D imutáveis. Toda operação devolve uma nova instância.

export class Vec2 {
  constructor(x = 0, y = 0) {
    this.x = x;
    this.y = y;
    Object.freeze(this);
  }
  static de([x, y]) { return new Vec2(x, y); }
  static deAngulo(rad, comprimento = 1) {
    return new Vec2(Math.cos(rad) * comprimento, Math.sin(rad) * comprimento);
  }
  soma(o) { return new Vec2(this.x + o.x, this.y + o.y); }
  sub(o) { return new Vec2(this.x - o.x, this.y - o.y); }
  escala(k) { return new Vec2(this.x * k, this.y * k); }
  dot(o) { return this.x * o.x + this.y * o.y; }
  /** Produto vetorial escalar (componente z). */
  cruz(o) { return this.x * o.y - this.y * o.x; }
  get norma() { return Math.hypot(this.x, this.y); }
  get normaQuad() { return this.x * this.x + this.y * this.y; }
  normalizado() {
    const n = this.norma;
    if (n === 0) throw new RangeError('vetor nulo não pode ser normalizado');
    return this.escala(1 / n);
  }
  perpendicular() { return new Vec2(-this.y, this.x); }
  rotaciona(rad) {
    const c = Math.cos(rad), s = Math.sin(rad);
    return new Vec2(this.x * c - this.y * s, this.x * s + this.y * c);
  }
  angulo() { return Math.atan2(this.y, this.x); }
  distancia(o) { return this.sub(o).norma; }
  lerp(o, t) { return new Vec2(this.x + (o.x - this.x) * t, this.y + (o.y - this.y) * t); }
  /** Projeção deste vetor sobre `o`. */
  projetaEm(o) {
    const d = o.normaQuad;
    if (d === 0) throw new RangeError('não é possível projetar sobre vetor nulo');
    return o.escala(this.dot(o) / d);
  }
  igual(o, eps = 0) { return Math.abs(this.x - o.x) <= eps && Math.abs(this.y - o.y) <= eps; }
  toArray() { return [this.x, this.y]; }
}

export class Vec3 {
  constructor(x = 0, y = 0, z = 0) {
    this.x = x;
    this.y = y;
    this.z = z;
    Object.freeze(this);
  }
  static de([x, y, z]) { return new Vec3(x, y, z); }
  soma(o) { return new Vec3(this.x + o.x, this.y + o.y, this.z + o.z); }
  sub(o) { return new Vec3(this.x - o.x, this.y - o.y, this.z - o.z); }
  escala(k) { return new Vec3(this.x * k, this.y * k, this.z * k); }
  dot(o) { return this.x * o.x + this.y * o.y + this.z * o.z; }
  cruz(o) {
    return new Vec3(
      this.y * o.z - this.z * o.y,
      this.z * o.x - this.x * o.z,
      this.x * o.y - this.y * o.x,
    );
  }
  get norma() { return Math.hypot(this.x, this.y, this.z); }
  normalizado() {
    const n = this.norma;
    if (n === 0) throw new RangeError('vetor nulo não pode ser normalizado');
    return this.escala(1 / n);
  }
  distancia(o) { return this.sub(o).norma; }
  lerp(o, t) {
    return new Vec3(this.x + (o.x - this.x) * t, this.y + (o.y - this.y) * t, this.z + (o.z - this.z) * t);
  }
  /** Rotação de Rodrigues em torno de um eixo arbitrário. */
  rotaciona(eixo, rad) {
    const k = eixo.normalizado();
    const c = Math.cos(rad), s = Math.sin(rad);
    return this.escala(c).soma(k.cruz(this).escala(s)).soma(k.escala(k.dot(this) * (1 - c)));
  }
  igual(o, eps = 0) {
    return Math.abs(this.x - o.x) <= eps && Math.abs(this.y - o.y) <= eps && Math.abs(this.z - o.z) <= eps;
  }
  toArray() { return [this.x, this.y, this.z]; }
}
