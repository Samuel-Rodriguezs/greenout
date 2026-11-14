// Currying que respeita a aridade (fn.length) e aceita aplicação parcial em qualquer agrupamento.

export const PLACEHOLDER = Symbol('placeholder');

export function curry(fn, aridade = fn.length) {
  const acumular = (recebidos) =>
    function (...novos) {
      // Preenche os placeholders primeiro, depois acrescenta o restante.
      const args = [...recebidos];
      const restantes = [...novos];
      for (let i = 0; i < args.length && restantes.length > 0; i++) {
        if (args[i] === PLACEHOLDER) args[i] = restantes.shift();
      }
      args.push(...restantes);

      const completos = args.slice(0, aridade).filter((a) => a !== PLACEHOLDER).length;
      if (args.length >= aridade && completos === aridade) return fn.apply(this, args);
      return acumular(args);
    };
  return acumular([]);
}
