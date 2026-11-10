// Helpers for putting data values into HTML strings safely.
// Layer names and paint options come from dataset (specification) data, so
// they must not be trusted as markup or CSS.

const HTML_ESCAPES = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

export const escapeHtml = (value) => {
  if (value === null || value === undefined) return '';
  return String(value).replace(/[&<>"']/g, (char) => HTML_ESCAPES[char]);
};

// Hex colours (#rgb, #rgba, #rrggbb, #rrggbbaa) or a plain colour name.
const SAFE_COLOUR = /^(#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})|[a-z]+)$/i;

export const safeCssColour = (value, fallback) => {
  if (typeof value !== 'string') return fallback;
  const colour = value.trim();
  return SAFE_COLOUR.test(colour) ? colour : fallback;
};

// A number between 0 and 1.
export const safeOpacity = (value, fallback) => {
  if (value === null || value === undefined || value === '') return fallback;
  const opacity = Number(value);
  if (Number.isNaN(opacity)) return fallback;
  return Math.min(1, Math.max(0, opacity));
};
