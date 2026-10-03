// Offline address lookup (port of the normalisation / match part of geo.py).
//
// The browser cannot call the US Census geocoder (no CORS), so lookups run against the saved
// Buffalo demo set, exactly like the Python app in offline mode (NOCO_OFFLINE=1).

export const BUFFALO_BBOX = [42.826, -78.92, 42.967, -78.795]; // south, west, north, east

const STREET_SUFFIXES = new Set(["ST", "AVE", "SQ", "BLVD", "RD", "DR", "PL", "PKWY", "TER", "CT", "LN", "WAY"]);
const PLACE_WORDS = new Set(["BUFFALO", "NY", "NEW", "YORK", "USA", "US"]);
const ABBREVIATIONS = {
  STREET: "ST",
  AVENUE: "AVE",
  SQUARE: "SQ",
  BOULEVARD: "BLVD",
  ROAD: "RD",
  DRIVE: "DR",
  PLACE: "PL",
  PARKWAY: "PKWY",
  TERRACE: "TER",
  COURT: "CT",
  LANE: "LN",
  NORTH: "N",
  SOUTH: "S",
  EAST: "E",
  WEST: "W",
};

export function inBuffalo(lat, lon) {
  const [south, west, north, east] = BUFFALO_BBOX;
  return south <= lat && lat <= north && west <= lon && lon <= east;
}

/** Street part only: '110 Franklin Street, Buffalo NY' -> '110 FRANKLIN ST'. */
export function normalizeAddress(address) {
  const words = address.toUpperCase().split(",")[0].replace(/[^A-Z0-9 ]/g, " ").split(/\s+/).filter(Boolean);
  // Without commas the city, state and ZIP trail the street: drop them, keeping number + street.
  while (words.length > 2 && (PLACE_WORDS.has(words.at(-1)) || /^\d{5}(\d{4})?$/.test(words.at(-1)))) {
    words.pop();
  }
  return words.map((w) => ABBREVIATIONS[w] || w).join(" ");
}

/** normalizeAddress without a trailing street suffix: '110 FRANKLIN ST' -> '110 FRANKLIN'. */
export function streetKey(address) {
  const words = normalizeAddress(address).split(" ").filter(Boolean);
  const drop = words.length > 2 && STREET_SUFFIXES.has(words.at(-1));
  return (drop ? words.slice(0, -1) : words).join(" ");
}

/**
 * The building whose street address equals `address` after normalisation, or null.
 * Whole-key equality, never substrings: "33 Franklin St" never finds "333 FRANKLIN ST".
 * Exact street first, then ignoring the suffix; an ambiguous suffix-less match returns null.
 */
export function matchAddress(address, buildings) {
  for (const normalize of [normalizeAddress, streetKey]) {
    const key = normalize(address);
    if (!key) return null;
    const found = buildings.filter((b) => normalize(b.address) === key);
    if (found.length === 1 || (found.length && normalize === normalizeAddress)) {
      return structuredClone(found[0]);
    }
  }
  return null;
}

/** Pre-fetched Buffalo buildings (a JSON list of BuildingFacts). */
export async function loadDemoBuildings(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Could not load ${url}: HTTP ${response.status}`);
  const data = await response.json();
  return Array.isArray(data) ? data : data.buildings || [];
}

/**
 * find_building from the pages: match the buildings on screen, then the saved demo set.
 * Returns null when the address is not in the saved data (the page shows a warning).
 */
export function findBuilding(address, available, demoSet = available) {
  if (!address.trim()) return null;
  return matchAddress(address, available) || matchAddress(address, demoSet);
}
