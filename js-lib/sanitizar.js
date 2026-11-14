const MAPA = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

// Escapa caracteres especiais de HTML.
export const escaparHtml = (s) => String(s).replace(/[&<>"']/g, (c) => MAPA[c]);
export const desescaparHtml = (s) =>
  String(s).replace(/&(lt|gt|quot|#39|amp);/g, (_, e) => ({ lt: '<', gt: '>', quot: '"', '#39': "'", amp: '&' })[e]);

// Remove todas as tags (e o conteúdo de script/style), deixando só texto.
export function removerTags(html) {
  return String(html)
    .replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<[^>]*>/g, '');
}
// Sanitiza para texto seguro: remove tags e escapa o restante.
export const sanitizarHtml = (html) => escaparHtml(removerTags(html));
