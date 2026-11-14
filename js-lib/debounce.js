// Adia a chamada até passarem `ms` sem novas invocações. Possui cancel().
export function debounce(fn, ms) {
  let timer = null;
  const deb = function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => { timer = null; fn.apply(this, args); }, ms);
  };
  deb.cancel = () => { clearTimeout(timer); timer = null; };
  return deb;
}
