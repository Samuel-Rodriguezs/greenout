export const rules = {
  required: (msg = 'Campo obrigatório') => (v) =>
    (v == null || (typeof v === 'string' && v.trim() === '') || (Array.isArray(v) && !v.length)) ? msg : null,
  minLength: (n, msg) => (v) => (String(v ?? '').length < n ? (msg ?? `Mínimo de ${n} caracteres`) : null),
  maxLength: (n, msg) => (v) => (String(v ?? '').length > n ? (msg ?? `Máximo de ${n} caracteres`) : null),
  pattern: (re, msg = 'Formato inválido') => (v) => (v === '' || v == null || re.test(String(v)) ? null : msg),
  email: (msg = 'E-mail inválido') => (v) =>
    (v === '' || v == null || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(v)) ? null : msg),
  min: (n, msg) => (v) => (v === '' || v == null || Number(v) >= n ? null : (msg ?? `Valor mínimo ${n}`)),
  max: (n, msg) => (v) => (v === '' || v == null || Number(v) <= n ? null : (msg ?? `Valor máximo ${n}`)),
  matches: (otherField, msg = 'Campos não conferem') => (v, all) => (v === all[otherField] ? null : msg),
  oneOf: (list, msg = 'Valor não permitido') => (v) => (list.includes(v) ? null : msg),
};

export function validateField(value, fieldRules, all = {}) {
  const errors = [];
  for (const rule of fieldRules) {
    const err = rule(value, all);
    if (err) errors.push(err);
  }
  return errors;
}

export function createValidator(schema) {
  return {
    validate(values) {
      const errors = {};
      for (const [field, fieldRules] of Object.entries(schema)) {
        const errs = validateField(values[field], fieldRules, values);
        if (errs.length) errors[field] = errs;
      }
      return { valid: Object.keys(errors).length === 0, errors };
    },
    async validateAsync(values) {
      const errors = {};
      for (const [field, fieldRules] of Object.entries(schema)) {
        const errs = [];
        for (const rule of fieldRules) {
          const e = await rule(values[field], values);
          if (e) errs.push(e);
        }
        if (errs.length) errors[field] = errs;
      }
      return { valid: Object.keys(errors).length === 0, errors };
    },
  };
}
