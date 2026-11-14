export function createToastQueue({ maxVisiveis = 3, duracao = 4000, onChange = () => {} } = {}) {
  let nextId = 1;
  let visiveis = [];
  const espera = [];
  const timers = new Map();

  const emit = () => onChange({ visiveis: [...visiveis], espera: espera.length });

  function mostrar(toast) {
    visiveis = [...visiveis, toast];
    if (toast.duracao > 0) {
      timers.set(toast.id, setTimeout(() => dispensar(toast.id), toast.duracao));
    }
  }

  function dispensar(id) {
    const i = visiveis.findIndex((t) => t.id === id);
    if (i === -1) {
      const w = espera.findIndex((t) => t.id === id);
      if (w >= 0) { espera.splice(w, 1); emit(); }
      return false;
    }
    clearTimeout(timers.get(id));
    timers.delete(id);
    visiveis = visiveis.filter((t) => t.id !== id);
    while (visiveis.length < maxVisiveis && espera.length) mostrar(espera.shift());
    emit();
    return true;
  }

  return {
    add(mensagem, { tipo = 'info', duracao: d = duracao, dedupe = true } = {}) {
      if (dedupe) {
        const dup = [...visiveis, ...espera].find((t) => t.mensagem === mensagem && t.tipo === tipo);
        if (dup) {
          dup.contagem++;
          if (timers.has(dup.id)) {
            clearTimeout(timers.get(dup.id));
            if (dup.duracao > 0) timers.set(dup.id, setTimeout(() => dispensar(dup.id), dup.duracao));
          }
          visiveis = [...visiveis];
          emit();
          return dup.id;
        }
      }
      const toast = { id: nextId++, mensagem, tipo, duracao: d, contagem: 1 };
      if (visiveis.length < maxVisiveis) mostrar(toast);
      else espera.push(toast);
      emit();
      return toast.id;
    },
    dismiss: dispensar,
    clear() {
      for (const t of timers.values()) clearTimeout(t);
      timers.clear();
      visiveis = [];
      espera.length = 0;
      emit();
    },
    get visiveis() { return [...visiveis]; },
    get naEspera() { return espera.length; },
  };
}
