import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const WORKSPACE = "/home/nguyenletuan/Desktop/NOCO_Scout_Pitch_work";
const SKILL_DIR = "/home/nguyenletuan/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations";
const TMP_DIR = path.join(WORKSPACE, "build");
const OUTPUT_DIR = "/home/nguyenletuan/Desktop/NOCO_Scout_Pitch";
const FINAL_PPTX = path.join(WORKSPACE, "output", "NOCO_Scout_Pitch_v2.pptx");
const DELIVERY_PPTX = path.join(OUTPUT_DIR, "NOCO_Scout_Pitch.pptx");
const RUNTIME_PYTHON = "/home/nguyenletuan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";

const { finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools/artifact_tool_utils.mjs")).href,
);

await fs.mkdir(TMP_DIR, { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });
await fs.mkdir(OUTPUT_DIR, { recursive: true });

const W = 1280;
const H = 720;
const FONT = "Noto Sans";
const BG = "#07110E";
const BG2 = "#0D1A16";
const FG = "#F5F8F6";
const MUTED = "#AAC0B7";
const ACCENT = "#2FD39A";
const ACCENT_DARK = "#0B7D5B";
const WARM = "#F69B62";

const assets = {
  logo: await fs.readFile("/home/nguyenletuan/Desktop/AI_FOR_GOOD/docs/pitch/assets/noco_logo.png"),
  addressPage: await fs.readFile(path.join(WORKSPACE, "assets/address_page.png")),
  addressMap: await fs.readFile(path.join(WORKSPACE, "assets/address_map_canvas.png")),
  addressEstimate: await fs.readFile(path.join(WORKSPACE, "assets/address_estimate_bottom.png")),
  prospectPage: await fs.readFile(path.join(WORKSPACE, "assets/prospect_ranked.png")),
  prospectMap: await fs.readFile(path.join(WORKSPACE, "assets/prospect_map_canvas.png")),
};

const deck = Presentation.create({ slideSize: { width: W, height: H } });

function addText(slide, text, x, y, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width, height },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 34,
    bold: options.bold ?? false,
    color: options.color ?? FG,
    alignment: options.alignment ?? "left",
    autoFit: "shrinkText",
  };
  return shape;
}

function addBox(slide, text, x, y, width, height, options = {}) {
  const shape = slide.shapes.add({
    geometry: options.geometry ?? "rect",
    position: { left: x, top: y, width, height },
    fill: options.fill ?? "none",
    line: options.line ?? { fill: "none", width: 0 },
  });
  if (text) {
    shape.text = text;
    shape.text.style = {
      typeface: FONT,
      fontSize: options.fontSize ?? 28,
      bold: options.bold ?? false,
      color: options.color ?? FG,
      alignment: options.alignment ?? "center",
      autoFit: "shrinkText",
    };
  }
  return shape;
}

function addImage(slide, bytes, alt, x, y, width, height, options = {}) {
  return slide.images.add({
    blob: bytes,
    contentType: "image/png",
    alt,
    fit: options.fit ?? "cover",
    position: { left: x, top: y, width, height },
    ...(options.crop ? { crop: options.crop } : {}),
    ...(options.geometry ? { geometry: options.geometry } : {}),
    ...(options.borderRadius ? { borderRadius: options.borderRadius } : {}),
  });
}

function addHeader(slide, title, number) {
  addText(slide, String(number).padStart(2, "0"), 62, 34, 66, 34, {
    fontSize: 22,
    bold: true,
    color: ACCENT,
  });
  addText(slide, title, 62, 70, 940, 78, { fontSize: 56, bold: true });
  addBox(slide, "", 62, 150, 94, 5, { fill: ACCENT });
}

function addFooter(slide, text = "") {
  if (text) {
    addText(slide, text, 62, 676, 940, 24, { fontSize: 16, color: MUTED });
  }
}

function addNotes(slide, lines) {
  slide.speakerNotes.textFrame.setText(Array.isArray(lines) ? lines.join("\n") : lines);
}

// 1. Title and hook
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addImage(
    slide,
    assets.prospectPage,
    "NOCO Scout offline prospect map with ranked Buffalo buildings and source-labelled details",
    0,
    0,
    W,
    H,
    { fit: "cover", crop: { left: 0.17, top: 0.07, right: 0, bottom: 0.06 } },
  );
  addBox(slide, "", 0, 0, W, H, {
    fill: "linear(90deg, #07110E/98 0%, #07110E/89 52%, #07110E/72 100%)",
  });
  addBox(slide, "", 0, 0, 12, H, { fill: ACCENT });
  addText(slide, "NOCO Scout", 76, 105, 770, 100, { fontSize: 78, bold: true });
  addText(
    slide,
    "From an address to a customer-ready quote in seconds.",
    80,
    218,
    690,
    140,
    { fontSize: 40, color: FG },
  );
  addText(slide, "AI for Good Hackathon\nNOCO challenge", 82, 520, 450, 70, {
    fontSize: 22,
    color: MUTED,
  });
  addText(
    slide,
    "Nguyen-Le-Tuan   Anh-08   phamvotriduc241106   NguyenQBao",
    82,
    620,
    930,
    32,
    { fontSize: 17, color: FG },
  );
  addText(slide, "(c) OpenStreetMap contributors", 930, 678, 300, 18, {
    fontSize: 14,
    color: MUTED,
    alignment: "right",
  });
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 0:00-0:15.",
    "Say: A NOCO rep today has to visit a building, collect data, and go back to the office before quoting. We do it from an address.",
    "Visual source: screenshot captured from the real offline NOCO Scout app. Map data: (c) OpenStreetMap contributors.",
  ]);
}

// 2. Problem
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addHeader(slide, "The quoting workflow today", 2);

  const steps = [
    { n: "01", label: "SITE VISIT" },
    { n: "02", label: "RESEARCH" },
    { n: "03", label: "QUOTE" },
  ];
  const boxes = steps.map((step, index) => {
    const x = 96 + index * 395;
    addText(slide, step.n, x, 245, 92, 64, { fontSize: 46, bold: true, color: ACCENT });
    return addBox(slide, step.label, x, 318, 270, 92, {
      fill: "none",
      line: { style: "solid", fill: "#517166", width: 2 },
      fontSize: 30,
      bold: true,
    });
  });
  addBox(slide, "", 394, 344, 64, 38, {
    geometry: "rightArrow",
    fill: ACCENT,
    line: { fill: "none", width: 0 },
  });
  addBox(slide, "", 789, 344, 64, 38, {
    geometry: "rightArrow",
    fill: ACCENT,
    line: { fill: "none", width: 0 },
  });
  addText(slide, "All of it takes time", 100, 492, 1080, 86, {
    fontSize: 52,
    bold: true,
    alignment: "center",
  });
  addFooter(slide, "Source: AI for Good briefing [03:49]-[04:13]");
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 0:15-0:40.",
    "Say: Your own team told us it takes time. A rep cannot visit every building in the city, so most are never quoted.",
    "Source: AI for Good briefing [03:49]-[04:13]. No unsupported claim about the number of days appears on the slide.",
  ]);
}

// 3. How it works
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addHeader(slide, "Address to quote", 3);

  const nodes = [
    ["ADDRESS", 86],
    ["CENSUS", 278],
    ["OSM", 470],
    ["BUFFALO", 662],
    ["CALCULATOR", 854],
    ["QUOTE", 1072],
  ];
  const circles = nodes.map(([label, x], index) => {
    const circle = addBox(slide, index === 0 || index === nodes.length - 1 ? "" : String(index), x, 270, 30, 30, {
      geometry: "ellipse",
      fill: index === 0 || index === nodes.length - 1 ? ACCENT : BG2,
      line: { style: "solid", fill: ACCENT, width: 3 },
      fontSize: 15,
      bold: true,
    });
    addText(slide, label, x - 55, 324, 140, 42, {
      fontSize: label === "CALCULATOR" ? 19 : 22,
      bold: true,
      alignment: "center",
      color: index === 0 || index === nodes.length - 1 ? FG : MUTED,
    });
    return circle;
  });
  for (let i = 0; i < circles.length - 1; i += 1) {
    slide.shapes.connect(circles[i], circles[i + 1], {
      kind: "straight",
      fromSide: "right",
      toSide: "left",
      line: { style: "solid", fill: "#517166", width: 3 },
    });
  }
  addText(slide, "Public data fills inputs. Every number shows its source.", 142, 448, 996, 96, {
    fontSize: 40,
    bold: true,
    alignment: "center",
  });
  addFooter(slide, "(c) OpenStreetMap contributors");
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 0:40-1:05.",
    "Say: Public map and property data give us perimeter, floors, and building type. Then we run the deterministic calculator based on NOCO's workbook.",
    "Sources: US Census Geocoder, OpenStreetMap, City of Buffalo Final Assessment Roll, and the supplied NOCO reference workbook.",
    "Map attribution: (c) OpenStreetMap contributors.",
  ]);
}

// 4. Live demo divider
{
  const slide = deck.slides.add();
  slide.background.fill = "#020504";
  addBox(slide, "", 152, 346, 976, 5, { fill: ACCENT });
  addText(slide, "Live demo", 150, 252, 980, 100, {
    fontSize: 80,
    bold: true,
    alignment: "center",
  });
  addText(slide, "110 seconds", 150, 382, 980, 42, {
    fontSize: 25,
    color: MUTED,
    alignment: "center",
  });
  addNotes(slide, [
    "Demo driver: NguyenQBao. Presenter keeps talking. Timing: 1:05-2:55.",
    "D1, about 40 seconds: Type the prepared Buffalo address. Show the 3D footprint and the Facts and confidence table. Click Estimate insulation upgrade. Point out that payback says needs installed cost when cost is unknown.",
    "D2, about 50 seconds: Open Prospect Map. Click Show potential customers. Hover two or three buildings. Click one building for details. Say: Hover anywhere and you see where each number comes from.",
    "D3, about 20 seconds: Open the customer report, then show the manager report and CSV controls. Keep the customer page visible for five seconds.",
    "Backup: If the app fails, switch to the prepared 60-second recording and say: Here is the recorded run.",
  ]);
}

// 5. Trust
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addHeader(slide, "Reference test", 4);
  addText(slide, "0.1%", 72, 210, 470, 165, { fontSize: 118, bold: true, color: ACCENT });
  addText(slide, "test tolerance", 78, 365, 430, 50, { fontSize: 28, color: MUTED });
  addText(slide, "Deterministic math", 624, 226, 520, 56, { fontSize: 38, bold: true });
  addBox(slide, "", 624, 300, 480, 2, { fill: "#517166" });
  addText(slide, "Source and confidence stay visible", 624, 325, 520, 56, {
    fontSize: 31,
    color: FG,
  });
  addText(slide, "Unknown cost stays unknown", 624, 420, 520, 56, {
    fontSize: 31,
    color: FG,
  });
  addText(
    slide,
    "Workbook values omitted because reuse permission remains unconfirmed.",
    72,
    610,
    1120,
    38,
    { fontSize: 20, color: WARM },
  );
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 2:55-3:15.",
    "Say: We tested the deterministic model against a reference case. The golden test passes within zero point one percent. Inputs, sources, and confidence remain visible, and unknown project cost stays unknown.",
    "Evidence: tests/test_noco_calc.py passed before export. The supplied workbook's permission statement remains unanswered, so this slide intentionally omits its values and screenshot.",
  ]);
}

// 6. Impact
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addHeader(slide, "One tool, three decisions", 5);
  addImage(
    slide,
    assets.prospectPage,
    "NOCO Scout prospect map showing ranked Buffalo buildings",
    680,
    120,
    600,
    520,
    { fit: "cover", crop: { left: 0.19, top: 0.31, right: 0.01, bottom: 0.02 } },
  );
  addBox(slide, "", 650, 120, 630, 520, { fill: "#07110E/58" });
  addText(slide, "300", 72, 192, 520, 160, { fontSize: 126, bold: true, color: ACCENT });
  addText(slide, "Buffalo buildings mapped", 78, 348, 500, 55, { fontSize: 35, bold: true });
  addText(slide, "REP\nquote", 82, 470, 145, 90, { fontSize: 22, bold: true, color: MUTED });
  addText(slide, "MANAGER\nranked prospects", 250, 470, 180, 90, {
    fontSize: 22,
    bold: true,
    color: MUTED,
  });
  addText(slide, "CUSTOMER\none page", 460, 470, 150, 90, {
    fontSize: 22,
    bold: true,
    color: MUTED,
  });
  addText(slide, "NOCO opportunity figures remain ILLUSTRATIVE.", 78, 632, 520, 28, {
    fontSize: 17,
    color: WARM,
  });
  addText(slide, "(c) OpenStreetMap contributors", 900, 678, 320, 18, {
    fontSize: 14,
    color: MUTED,
    alignment: "right",
  });
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 3:15-3:30.",
    "Say: The same tool serves the rep, the manager, and the building owner. Our offline demo dataset contains 300 Buffalo buildings ready to rank.",
    "Evidence: data/public/demo_buildings.json contains 300 public-data records. NOCO opportunity figures remain illustrative until NOCO provides cost and margin definitions.",
    "Map attribution: (c) OpenStreetMap contributors.",
  ]);
}

// 7. Innovation and future
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addHeader(slide, "The same pipeline extends", 6);
  addImage(
    slide,
    assets.addressPage,
    "NOCO Scout address screen with a sourced building footprint and confidence table",
    68,
    198,
    520,
    350,
    { fit: "cover", crop: { left: 0.20, top: 0.29, right: 0.02, bottom: 0.02 } },
  );
  addBox(slide, "", 68, 198, 520, 350, { fill: "#07110E/26" });
  addText(slide, "GIS inputs", 660, 205, 500, 52, { fontSize: 38, bold: true, color: ACCENT });
  addText(slide, "Provenance on hover", 660, 292, 500, 52, { fontSize: 34, bold: true });
  addText(slide, "Citywide prospecting", 660, 376, 500, 52, { fontSize: 34, bold: true });
  addBox(slide, "", 660, 456, 470, 2, { fill: "#517166" });
  addText(slide, "Next: windows   HVAC   solar   CRM   more cities", 660, 488, 500, 88, {
    fontSize: 27,
    color: MUTED,
  });
  addText(slide, "(c) OpenStreetMap contributors", 68, 678, 310, 18, {
    fontSize: 14,
    color: MUTED,
  });
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 3:30-3:50.",
    "Say: Insulation is the first measure. The same pipeline extends to windows, HVAC, solar, more incentives, and every city NOCO serves. A future CRM connection can put ranked prospects into the sales workflow.",
    "Future items are roadmap concepts, not features in the current demo. Disadvantaged-community targeting requires a verified public classification source before implementation.",
    "Map attribution: (c) OpenStreetMap contributors.",
  ]);
}

// 8. Close and ask
{
  const slide = deck.slides.add();
  slide.background.fill = BG;
  addBox(slide, "", 0, 0, 12, H, { fill: ACCENT });
  addText(slide, "Pilot", 80, 80, 360, 68, { fontSize: 46, bold: true, color: MUTED });
  addText(slide, "50", 76, 150, 430, 210, { fontSize: 168, bold: true, color: ACCENT });
  addText(slide, "Buffalo buildings", 82, 352, 550, 70, { fontSize: 48, bold: true });
  addText(slide, "One week with the NOCO sales team", 82, 448, 580, 62, {
    fontSize: 32,
    color: FG,
  });
  addBox(slide, "", 770, 154, 420, 250, { fill: "#F5F8F6" });
  addImage(slide, assets.logo, "NOCO logo", 790, 178, 380, 200, { fit: "contain" });
  addText(slide, "Thank you", 780, 428, 410, 70, { fontSize: 50, bold: true, alignment: "center" });
  addText(
    slide,
    "Nguyen-Le-Tuan   Anh-08\nphamvotriduc241106   NguyenQBao",
    760,
    535,
    450,
    64,
    { fontSize: 19, color: MUTED, alignment: "center" },
  );
  addNotes(slide, [
    "Presenter: Nguyen-Le-Tuan. Timing: 3:50-4:00.",
    "Say: Give us 50 buildings and a week, and we will show your reps what a quote from an address looks like. Thank you.",
    "The 50-building pilot is the team's proposed next step, not an existing commitment from NOCO.",
  ]);
}

const stagingDir = path.join(WORKSPACE, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(deck)).save(candidatePath);

const requirements = {
  explicitTotalSlideCount: 8,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const fontPolicy = { basis: "design", families: [FONT] };
const result = await finalizePresentation({
  ...requirements,
  workspaceDir: WORKSPACE,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu",
    "12192000,6858000",
    "--validate-bullet-geometry",
    "--validate-heading-fit",
  ],
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "NOCO_Scout_Pitch_v2.pptx.validation.json"),
});
await fs.copyFile(FINAL_PPTX, DELIVERY_PPTX);

for (let index = 0; index < deck.slides.items.length; index += 1) {
  const slide = deck.slides.items[index];
  const preview = await deck.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(
    path.join(TMP_DIR, `slide-${String(index + 1).padStart(2, "0")}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

console.log(JSON.stringify({ finalPath: DELIVERY_PPTX, validation: result }, null, 2));
