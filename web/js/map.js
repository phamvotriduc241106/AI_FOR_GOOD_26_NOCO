// Buffalo 3D map. deck.gl + MapLibre (CARTO dark basemap) when the CDN scripts load;
// otherwise a dependency-free SVG map with the same hover tooltips and click selection.

const CARTO_DARK = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";
const UNRANKED = [70, 133, 168, 185];
const LINE = [160, 196, 206, 140];

// `?map=svg` forces the dependency-free map (no WebGL / no CDN), e.g. on a locked-down projector.
export const hasDeck = () =>
  typeof window !== "undefined" && !!window.deck && new URLSearchParams(location.search).get("map") !== "svg";

/** View like the Streamlit pages: centred on the buildings, or on one address. */
export function viewFor(prospects, center = null) {
  if (center) return { latitude: center[0], longitude: center[1], zoom: 16.5, pitch: 50, bearing: -15 };
  const n = prospects.length || 1;
  const lat = prospects.reduce((s, p) => s + p.facts.lat, 0) / n;
  const lon = prospects.reduce((s, p) => s + p.facts.lon, 0) / n;
  const zoom = prospects.length === 1 ? 16.3 : prospects.length <= 10 ? 15.0 : 12.6;
  return { latitude: lat, longitude: lon, zoom, pitch: 50, bearing: -15 };
}

export class BuildingMap {
  /** @param {HTMLElement} el  @param {{onSelect?: (index:number)=>void, offline?: boolean}} opts */
  constructor(el, { onSelect = () => {}, offline = false } = {}) {
    this.el = el;
    this.onSelect = onSelect;
    this.offline = offline;
    this.mode = hasDeck() ? "deck" : "svg";
    this.rows = [];
    this.selected = null;
    if (this.mode === "deck") this.initDeck();
    else this.initSvg();
  }

  initDeck() {
    const { DeckGL } = window.deck;
    const basemap = !this.offline && !!window.maplibregl;
    this.deck = new DeckGL({
      container: this.el,
      mapStyle: basemap ? CARTO_DARK : null,
      initialViewState: { latitude: 42.888, longitude: -78.875, zoom: 12.6, pitch: 50, bearing: -15 },
      controller: true,
      layers: [],
      getTooltip: ({ object }) =>
        object && {
          html: object.tooltip_html,
          style: {
            backgroundColor: "rgba(20, 38, 44, 0.96)",
            color: "#E7F1F3",
            fontSize: "12px",
            lineHeight: "1.4",
            maxWidth: "300px",
            whiteSpace: "normal",
            border: "1px solid #2DD4BF",
            borderRadius: "10px",
            padding: "10px 12px",
          },
        },
      onClick: ({ object }) => object && this.onSelect(object.prospect_index),
    });
    if (!basemap) this.el.style.background = "#0a161a";
  }

  initSvg() {
    this.el.innerHTML = "";
    this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.svg.classList.add("fallback-svg");
    this.tooltip = document.createElement("div");
    this.tooltip.className = "map-tooltip";
    this.tooltip.hidden = true;
    this.el.append(this.svg, this.tooltip);
    this.view = null;
    let drag = null;
    this.svg.addEventListener("wheel", (e) => {
      if (!this.view) return;
      e.preventDefault();
      const r = this.svg.getBoundingClientRect();
      const f = e.deltaY > 0 ? 1.15 : 1 / 1.15;
      const mx = this.view.x + ((e.clientX - r.left) / r.width) * this.view.w;
      const my = this.view.y + ((e.clientY - r.top) / r.height) * this.view.h;
      this.view = { x: mx - (mx - this.view.x) * f, y: my - (my - this.view.y) * f, w: this.view.w * f, h: this.view.h * f };
      this.applyView();
    }, { passive: false });
    this.svg.addEventListener("pointerdown", (e) => {
      drag = { x: e.clientX, y: e.clientY, view: { ...this.view }, moved: false };
    });
    window.addEventListener("pointerup", () => { drag = null; });
    this.svg.addEventListener("pointermove", (e) => {
      if (drag && this.view) {
        const r = this.svg.getBoundingClientRect();
        const dx = ((e.clientX - drag.x) / r.width) * drag.view.w;
        const dy = ((e.clientY - drag.y) / r.height) * drag.view.h;
        if (Math.abs(dx) + Math.abs(dy) > 0) drag.moved = true;
        this.view = { ...drag.view, x: drag.view.x - dx, y: drag.view.y - dy };
        this.applyView();
      }
      const target = e.target.closest("path");
      if (target && !drag) {
        const row = this.rows[Number(target.dataset.i)];
        const box = this.el.getBoundingClientRect();
        this.tooltip.innerHTML = row.tooltip_html;
        this.tooltip.hidden = false;
        const x = Math.min(e.clientX - box.left + 14, box.width - 310);
        this.tooltip.style.left = `${Math.max(8, x)}px`;
        this.tooltip.style.top = `${e.clientY - box.top + 14}px`;
      } else if (!target) this.tooltip.hidden = true;
    });
    this.svg.addEventListener("pointerleave", () => { this.tooltip.hidden = true; });
    this.svg.addEventListener("click", (e) => {
      const target = e.target.closest("path");
      if (target) this.onSelect(this.rows[Number(target.dataset.i)].prospect_index);
    });
  }

  applyView() {
    const { x, y, w, h } = this.view;
    this.svg.setAttribute("viewBox", `${x} ${y} ${w} ${h}`);
  }

  /** Draw rows from prospectsToDeckRows(); ranked=false paints every building the same colour. */
  update(rows, view, { ranked = true, padding = null } = {}) {
    this.rows = rows.map((row) => (ranked ? row : { ...row, color: UNRANKED }));
    this.padding = padding;
    if (this.mode === "deck") this.updateDeck(view);
    else this.updateSvg(view);
  }

  /** Frame every building, leaving room for the floating panels (deck.gl only). */
  fitView(view, padding) {
    const { WebMercatorViewport } = window.deck;
    if (!padding || this.rows.length < 2 || !WebMercatorViewport) return view;
    let minLon = Infinity, minLat = Infinity, maxLon = -Infinity, maxLat = -Infinity;
    for (const row of this.rows) {
      for (const [lon, lat] of row.polygon) {
        minLon = Math.min(minLon, lon); maxLon = Math.max(maxLon, lon);
        minLat = Math.min(minLat, lat); maxLat = Math.max(maxLat, lat);
      }
    }
    const { width, height } = this.el.getBoundingClientRect();
    if (width < 400 || height < 300) return view;
    try {
      const fitted = new WebMercatorViewport({ width, height }).fitBounds(
        [[minLon, minLat], [maxLon, maxLat]],
        { padding },
      );
      return { ...view, latitude: fitted.latitude, longitude: fitted.longitude, zoom: Math.min(fitted.zoom, 17) };
    } catch {
      return view;
    }
  }

  updateDeck(view) {
    view = this.fitView(view, this.padding);
    const { PolygonLayer } = window.deck;
    const layer = new PolygonLayer({
      id: "noco-buildings",
      data: this.rows,
      getPolygon: (d) => d.polygon,
      getFillColor: (d) => d.color,
      getLineColor: LINE,
      getLineWidth: 1,
      lineWidthUnits: "pixels",
      getElevation: (d) => d.elevation,
      elevationScale: 1,
      extruded: true,
      wireframe: true,
      pickable: true,
      autoHighlight: true,
      highlightColor: [45, 212, 191, 200],
      stroked: true,
    });
    const viewKey = JSON.stringify(view);
    const props = { layers: [layer] };
    if (viewKey !== this.viewKey) {
      props.initialViewState = { ...view, transitionDuration: 900 };
      this.viewKey = viewKey;
    }
    this.deck.setProps(props);
  }

  updateSvg(view) {
    const ns = "http://www.w3.org/2000/svg";
    this.svg.innerHTML = "";
    if (!this.rows.length) return;
    const lat0 = view ? view.latitude : 42.89;
    const kx = Math.cos((lat0 * Math.PI) / 180);
    const project = ([lon, lat]) => [lon * kx * 1e4, -lat * 1e4];
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    const shapes = this.rows.map((row) => {
      const pts = row.polygon.map(project);
      for (const [x, y] of pts) {
        minX = Math.min(minX, x); maxX = Math.max(maxX, x);
        minY = Math.min(minY, y); maxY = Math.max(maxY, y);
      }
      return pts;
    });
    // Taller buildings drawn last, with a soft offset "shadow" to hint at height.
    const order = this.rows.map((_, i) => i).sort((a, b) => this.rows[a].elevation - this.rows[b].elevation);
    for (const i of order) {
      const row = this.rows[i];
      const pts = shapes[i];
      const lift = Math.min(row.elevation, 120) * 0.012;
      const d = (dx, dy) => "M" + pts.map(([x, y]) => `${(x + dx).toFixed(3)},${(y + dy).toFixed(3)}`).join("L") + "Z";
      const shadow = document.createElementNS(ns, "path");
      shadow.setAttribute("d", d(lift, lift));
      shadow.setAttribute("fill", "rgba(0,0,0,0.45)");
      shadow.style.pointerEvents = "none";
      shadow.style.stroke = "none";
      const path = document.createElementNS(ns, "path");
      path.setAttribute("d", d(0, -lift));
      const [r, g, b, a] = row.color;
      path.setAttribute("fill", `rgba(${r},${g},${b},${a / 255})`);
      path.dataset.i = String(i);
      if (this.selected === row.prospect_index) path.classList.add("selected");
      this.svg.append(shadow, path);
    }
    const w = Math.max(maxX - minX, 1e-3);
    const h = Math.max(maxY - minY, 1e-3);
    const box = this.el.getBoundingClientRect();
    const width = box.width || 800;
    const height = box.height || 560;
    // Same framing as deck.gl: fit the buildings inside the area left free by the panels.
    const p = typeof this.padding === "number"
      ? { top: this.padding, bottom: this.padding, left: this.padding, right: this.padding }
      : { top: 30, bottom: 30, left: 30, right: 30, ...(this.padding || {}) };
    const freeW = Math.max(width - p.left - p.right, 120);
    const freeH = Math.max(height - p.top - p.bottom, 120);
    // A single building gets a neighbourhood-sized frame instead of filling the screen.
    const unitsPerPx = Math.max(w / freeW, h / freeH) * (this.rows.length === 1 ? 6 : 1.08);
    const cx = (minX + maxX) / 2;
    const cy = (minY + maxY) / 2;
    this.view = {
      x: cx - (p.left + freeW / 2) * unitsPerPx,
      y: cy - (p.top + freeH / 2) * unitsPerPx,
      w: width * unitsPerPx,
      h: height * unitsPerPx,
    };
    this.applyView();
  }

  setSelected(prospectIndex) {
    this.selected = prospectIndex;
    if (this.mode === "svg") {
      this.svg.querySelectorAll("path.selected").forEach((p) => p.classList.remove("selected"));
      const i = this.rows.findIndex((r) => r.prospect_index === prospectIndex);
      const path = this.svg.querySelector(`path[data-i="${i}"]`);
      if (path) path.classList.add("selected");
    }
  }

  destroy() {
    if (this.deck) this.deck.finalize();
    this.el.innerHTML = "";
  }
}
