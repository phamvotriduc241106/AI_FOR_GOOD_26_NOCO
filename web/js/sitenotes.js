// AI site notes (port of the noco_scout feature in __init__.py + hackkit pipeline/export).
//
// The LLM only extracts stated facts; numbers are never decided by the model. In the browser
// there is no safe place for an API key, so the page replays the feature's sample response
// (the same as `make demo`, LLM_PROVIDER=fake) and runs the deterministic checks on it.

export const TITLE = "NOCO Address-to-Quote (Buffalo)";
export const DESCRIPTION = "Extracts stated facts from synthetic or public text for human review.";

export const FACT_FIELDS = [
  "address",
  "building_use",
  "floors",
  "year_built",
  "heating_system",
  "existing_insulation_r",
  "monthly_bill_usd",
];
const CHECKED = ["address", "heating_system", "existing_insulation_r"];
const FIELD_ORDER = ["confidence", "uncertain_fields", ...FACT_FIELDS, "evidence"];

// Synthetic note: made-up address and numbers, safe to send to any LLM provider.
export const SAMPLE_TEXT = `Site visit, 101 Example Main St, Buffalo NY (synthetic note).
Six-storey office building, built 1962. Heating is electric resistance baseboard.
Walls have R-11 batts per the facilities manager. Last electric bill was $4,250 for the month.`;

export const SAMPLE_RESPONSE = JSON.stringify({
  address: "101 Example Main St, Buffalo NY",
  building_use: "office",
  floors: 6,
  year_built: 1962,
  heating_system: "electric resistance baseboard",
  existing_insulation_r: 11,
  monthly_bill_usd: 4250.0,
  evidence: SAMPLE_TEXT,
  confidence: 0.85,
  uncertain_fields: [],
});

const isInt = (v) => typeof v === "number" && Number.isInteger(v);
const isNum = (v) => typeof v === "number" && Number.isFinite(v);

/** SiteNote.model_validate: strict types, ranges, extra="forbid". Returns {ok, data, error}. */
export function validateSiteNote(raw) {
  const errors = [];
  if (raw === null || typeof raw !== "object" || Array.isArray(raw)) {
    return { ok: false, data: null, error: "Model output is not a JSON object." };
  }
  for (const key of Object.keys(raw)) {
    if (!FIELD_ORDER.includes(key)) errors.push(`${key}: extra fields are not permitted`);
  }
  const data = {
    confidence: 1.0,
    uncertain_fields: [],
    address: null,
    building_use: null,
    floors: null,
    year_built: null,
    heating_system: null,
    existing_insulation_r: null,
    monthly_bill_usd: null,
    evidence: "",
  };
  const text = (key) => {
    const v = raw[key];
    if (v === undefined || v === null) return null;
    if (typeof v !== "string") {
      errors.push(`${key}: must be text`);
      return null;
    }
    return v.trim() || null; // empty text does not count as an extracted fact
  };
  data.address = text("address");
  data.building_use = text("building_use");
  data.heating_system = text("heating_system");

  const strictInt = (key, min, max) => {
    const v = raw[key];
    if (v === undefined || v === null) return null;
    if (!isInt(v)) errors.push(`${key}: must be a whole number`);
    else if (v < min || v > max) errors.push(`${key}: out of range`);
    else return v;
    return null;
  };
  data.floors = strictInt("floors", 1, Infinity);
  data.year_built = strictInt("year_built", 1, 9999);

  const strictNum = (key, check, message) => {
    const v = raw[key];
    if (v === undefined || v === null) return null;
    if (!isNum(v)) errors.push(`${key}: must be a finite number`);
    else if (!check(v)) errors.push(`${key}: ${message}`);
    else return v;
    return null;
  };
  data.existing_insulation_r = strictNum("existing_insulation_r", (v) => v > 0, "must be greater than 0");
  data.monthly_bill_usd = strictNum("monthly_bill_usd", (v) => v >= 0, "must be at least 0");

  if (raw.evidence !== undefined && raw.evidence !== null) {
    if (typeof raw.evidence !== "string") errors.push("evidence: must be text");
    else data.evidence = raw.evidence;
  }
  if (raw.confidence !== undefined) {
    if (!isNum(raw.confidence) || raw.confidence < 0 || raw.confidence > 1) {
      errors.push("confidence: must be between 0 and 1");
    } else data.confidence = raw.confidence;
  }
  if (raw.uncertain_fields !== undefined) {
    const list = raw.uncertain_fields;
    if (!Array.isArray(list) || list.some((x) => typeof x !== "string")) {
      errors.push("uncertain_fields: must be a list of field names");
    } else if (list.some((x) => ![...FACT_FIELDS, "evidence"].includes(x))) {
      errors.push("uncertain_fields: must name SiteNote facts or evidence");
    } else data.uncertain_fields = [...new Set(list)];
  }
  if (errors.length) return { ok: false, data: null, error: errors.join("; ") };
  return { ok: true, data, error: null };
}

/** Deterministic checks only; savings come from calc.js, never from the model. */
export function rules(note) {
  const flags = CHECKED.filter((name) => note[name] === null).map((field) => ({
    field,
    reason: "Not stated in the note; confirm before estimating.",
  }));
  const found = FACT_FIELDS.filter((name) => note[name] !== null).length;
  if (found && !note.evidence.trim()) {
    flags.push({ field: "evidence", reason: "No supporting source sentences were copied." });
  }
  return {
    metrics: { fields_found: found },
    flags,
    summary: `Site note for ${note.address || "an unknown address"}.`,
  };
}

/** hackkit.schemas.review_flags_for: the model's own uncertainty as review flags. */
export function reviewFlagsFor(note, threshold = 0.6) {
  const flags = note.uncertain_fields.map((field) => ({
    field,
    reason: "Model marked this field as uncertain.",
  }));
  if (note.confidence < threshold) {
    flags.push({ field: "*", reason: `Low overall confidence (${note.confidence.toFixed(2)}).` });
  }
  return flags;
}

/** run_feature with the fake provider: replay the sample response, validate, apply rules. */
export function runFeature(_text, responder = () => SAMPLE_RESPONSE) {
  const rawText = responder(_text);
  let parsed;
  try {
    parsed = JSON.parse(rawText);
  } catch {
    return { ok: false, error: "Model output is not valid JSON.", rawText, attempts: 1 };
  }
  const validated = validateSiteNote(parsed);
  if (!validated.ok) return { ok: false, error: validated.error, rawText, attempts: 1 };
  const ruleResult = rules(validated.data);
  return {
    ok: true,
    data: validated.data,
    rules: ruleResult,
    flags: [...reviewFlagsFor(validated.data), ...ruleResult.flags],
    attempts: 1,
  };
}

const pad = (n) => String(n).padStart(2, "0");

export function toJson(result, now = new Date()) {
  const stamp =
    `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T` +
    `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  return JSON.stringify(
    {
      feature: "noco_scout",
      generated_at: stamp,
      data: result.ok ? result.data : null,
      metrics: result.ok ? result.rules.metrics : {},
      flags: result.ok ? result.flags : [],
      error: result.ok ? null : result.error,
    },
    null,
    2,
  );
}

export function toMarkdown(result, now = new Date()) {
  const lines = [`# ${TITLE}`, ""];
  lines.push(
    `Generated ${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
      `${pad(now.getHours())}:${pad(now.getMinutes())}.`,
  );
  lines.push("");
  if (result.ok && result.rules.summary) lines.push(result.rules.summary, "");
  if (result.ok && Object.keys(result.rules.metrics).length) {
    lines.push("## Key numbers", "");
    for (const [name, value] of Object.entries(result.rules.metrics)) lines.push(`- ${name}: ${value}`);
    lines.push("");
  }
  lines.push("## Needs human review", "");
  const flags = result.ok ? result.flags : [];
  lines.push(...(flags.length ? flags.map((f) => `- ${f.field}: ${f.reason}`) : ["- Nothing flagged."]));
  lines.push("");
  if (result.ok) {
    lines.push("## Extracted data", "", "```json", JSON.stringify(result.data, null, 2), "```", "");
  }
  return lines.join("\n");
}
