// Shared wiring for the guide pages: reads the form, validates ranges, keeps the
// figures in the URL so a result can be shared, and calls the page's render().
export const gbp0 = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', maximumFractionDigits: 0 });
export const gbp2 = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP', minimumFractionDigits: 2, maximumFractionDigits: 2 });
export const $ = (id) => document.getElementById(id);
const num = (v) => Number(String(v).replace(/[£,%\s]/g, ''));
export const plain = (n) => (Number.isInteger(n) ? String(n) : String(+n.toFixed(2)));

export function duration(months) {
  const m = Math.round(months);
  const y = Math.floor(m / 12), r = m % 12;
  const parts = [];
  if (y) parts.push(`${y} year${y === 1 ? '' : 's'}`);
  if (r) parts.push(`${r} month${r === 1 ? '' : 's'}`);
  return parts.join(' ') || '0 months';
}

/**
 * fields: { id: { min, max, money?, text?, msg? } }  (text: a <select> with string values)
 * check(values) -> extra errors { id: message }
 * render(values) is called with valid values; showInvalid() when anything is wrong.
 */
export function setup({ fields, defaults, check = () => ({}), render, showInvalid }) {
  const ids = Object.keys(fields);
  const show = (id, v) => {
    const f = fields[id];
    $(id).value = f.text ? v : f.money ? Number(v).toLocaleString('en-GB') : plain(Number(v));
  };
  let start = defaults;
  try {
    const q = new URLSearchParams(location.search);
    if (ids.every((k) => q.has(k))) {
      const d = {};
      for (const k of ids) d[k] = fields[k].text ? q.get(k) : num(q.get(k));
      if (ids.every((k) => fields[k].text || Number.isFinite(d[k]))) start = d;
    }
  } catch (_) {}
  for (const k of ids) show(k, start[k]);

  function read() {
    const d = {};
    for (const k of ids) d[k] = fields[k].text ? $(k).value : $(k).value.trim() === '' ? NaN : num($(k).value);
    return d;
  }

  function run() {
    const d = read();
    const errors = {};
    for (const k of ids) {
      const f = fields[k];
      if (f.text) continue;
      if (!(d[k] >= f.min && d[k] <= f.max)) {
        const fmt = (x) => (f.money ? gbp0.format(x) : plain(x));
        errors[k] = f.msg || `Enter a number from ${fmt(f.min)} to ${fmt(f.max)}`;
      }
    }
    if (!Object.keys(errors).length) Object.assign(errors, check(d));
    for (const k of ids) {
      const e = $(`e-${k}`);
      if (e) e.textContent = errors[k] || '';
      $(`f-${k}`)?.classList.toggle('bad', !!errors[k]);
    }
    if (Object.keys(errors).length) { showInvalid?.(); return; }
    try {
      const q = new URLSearchParams();
      for (const k of ids) q.set(k, fields[k].text ? d[k] : plain(d[k]));
      history.replaceState(null, '', `${location.pathname}?${q}`);
    } catch (_) {}
    render(d);
  }

  const form = $('form');
  form.addEventListener('input', run);
  form.addEventListener('change', run);
  form.addEventListener('submit', (e) => e.preventDefault());
  run();
}

/** Link to the main calculator with these figures filled in. */
export function fullCalculatorLink(d) {
  const q = new URLSearchParams();
  for (const k of ['loan', 'termYears', 'dealRate', 'dealYears', 'svr', 'overpayment']) q.set(k, plain(d[k]));
  return `../?${q}`;
}
