// Python-compatible number and text formatting.
//
// The calculator labels ("HDD=6750"), reports ("$1,448") and CSV ("15600.0") were designed in
// Python, so the browser must format numbers exactly like Python does: correctly rounded on the
// exact binary value, ties to even, `g` with 6 significant digits, `repr` for CSV floats.

/** Exact decimal expansion of a finite double as {neg, n: BigInt, k} with |x| = n × 10^-k. */
function exact(x) {
  const neg = x < 0 || Object.is(x, -0);
  const s = Math.abs(x).toPrecision(100); // exact for the magnitudes used in this app
  let [mantissa, exp] = s.split("e");
  exp = exp === undefined ? 0 : Number(exp);
  const [intPart, frac = ""] = mantissa.split(".");
  const n = BigInt(intPart + frac);
  return { neg, n, k: frac.length - exp };
}

const TEN = 10n;
const pow10 = (e) => TEN ** BigInt(e);

/** round(|x| × 10^nd) as BigInt, ties to even (Python's correctly rounded formatting). */
function scaledRound(x, nd) {
  const { n, k } = exact(x);
  const shift = nd - k;
  if (shift >= 0) return n * pow10(shift);
  const div = pow10(-shift);
  const q = n / div;
  const r = n % div;
  const twice = 2n * r;
  if (twice > div || (twice === div && q % 2n === 1n)) return q + 1n;
  return q;
}

function groupThousands(intDigits) {
  return intDigits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/** Python f"{x:.{nd}f}" (or f"{x:,.{nd}f}" with comma=true). */
export function fixed(x, nd = 0, comma = false) {
  if (!Number.isFinite(x)) return String(x);
  const q = scaledRound(x, nd);
  let digits = q.toString().padStart(nd + 1, "0");
  let intPart = nd ? digits.slice(0, -nd) : digits;
  const fracPart = nd ? digits.slice(-nd) : "";
  if (comma) intPart = groupThousands(intPart);
  const neg = (x < 0 || Object.is(x, -0)) ? "-" : "";
  return neg + intPart + (nd ? "." + fracPart : "");
}

/** Python f"{x:,.0f}" — money and counts in reports. */
export const comma0 = (x) => fixed(x, 0, true);

/** Python f"{x:g}" (precision 6). */
export function g(x, precision = 6) {
  if (Number.isInteger(x) && typeof x === "number" && Math.abs(x) < 1e6) return String(x);
  if (x === 0) return Object.is(x, -0) ? "-0" : "0";
  if (!Number.isFinite(x)) return x > 0 ? "inf" : x < 0 ? "-inf" : "nan";
  const neg = x < 0 ? "-" : "";
  const ax = Math.abs(x);
  const { n, k } = exact(ax);
  let e = n.toString().length - 1 - k; // decimal exponent of the leading digit
  let q = scaledRound(ax, precision - 1 - e);
  if (q.toString().length > precision) {
    e += 1; // rounding carried into a new leading digit (e.g. 999999.5)
    q = scaledRound(ax, precision - 1 - e);
  }
  const digits = q.toString().padStart(precision, "0");
  if (e >= -4 && e < precision) {
    const nd = precision - 1 - e;
    let out = fixed(ax, Math.max(nd, 0));
    if (out.includes(".")) out = out.replace(/0+$/, "").replace(/\.$/, "");
    return neg + out;
  }
  let mant = digits[0] + (digits.length > 1 ? "." + digits.slice(1) : "");
  mant = mant.replace(/0+$/, "").replace(/\.$/, "");
  const sign = e < 0 ? "-" : "+";
  return `${neg}${mant}e${sign}${String(Math.abs(e)).padStart(2, "0")}`;
}

/** Python round(x, nd) for floats (ties to even on the exact value). */
export function pyRound(x, nd = 0) {
  if (!Number.isFinite(x)) return x;
  const q = scaledRound(x, nd);
  const v = Number(q) / 10 ** nd;
  return x < 0 ? -v : v;
}

/** Python round(x) -> int (ties to even). */
export function pyRoundInt(x) {
  return pyRound(x, 0) + 0;
}

/** Python repr(float): shortest round-trip digits, always with a decimal point or exponent. */
export function floatRepr(x) {
  if (!Number.isFinite(x)) return x > 0 ? "inf" : x < 0 ? "-inf" : "nan";
  if (Object.is(x, -0)) return "-0.0";
  const ax = Math.abs(x);
  if (ax !== 0 && (ax < 1e-4 || ax >= 1e16)) {
    const [m, e] = x.toExponential().split("e");
    const exp = Number(e);
    return `${m}e${exp < 0 ? "-" : "+"}${String(Math.abs(exp)).padStart(2, "0")}`;
  }
  const s = String(x);
  return /[.e]/.test(s) ? s : s + ".0";
}

/** Python f"{x:.0%}". */
export const percent0 = (x) => fixed(x * 100, 0) + "%";

/** Python html.escape(s, quote=True). */
export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

/** Python sort order for strings (code points, not locale). */
export function cmpStr(a, b) {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Python dict.fromkeys(items): unique, first-seen order. */
export const uniqueInOrder = (items) => [...new Set(items)];

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

/** Python f"{date:%B %d, %Y}". */
export function longDate(d) {
  return `${MONTHS[d.getMonth()]} ${String(d.getDate()).padStart(2, "0")}, ${d.getFullYear()}`;
}
