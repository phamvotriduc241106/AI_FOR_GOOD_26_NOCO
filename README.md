<p align="center">
  <img src="docs/pitch/assets/noco_scout_readme_hero.png" alt="NOCO Scout maps Buffalo buildings from an address to an energy opportunity" width="100%">
</p>

<h1 align="center">NOCO Scout</h1>

<p align="center"><strong>From a Buffalo address to a customer-ready insulation estimate in seconds.</strong></p>

<p align="center">
  <a href="https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/Nguyen-Le-Tuan/AI_FOR_GOOD/ci.yml?branch=main&style=flat-square&label=CI&color=00A68A" alt="CI status"></a>
  <img src="https://img.shields.io/badge/Python-3.11%2B-00A68A?style=flat-square&logo=python&logoColor=white" alt="Python 3.11 or newer">
  <img src="https://img.shields.io/badge/Streamlit-app-F59E0B?style=flat-square&logo=streamlit&logoColor=white" alt="Streamlit app">
  <img src="https://img.shields.io/badge/demo-offline--ready-00A68A?style=flat-square" alt="Offline-ready demo">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-102731?style=flat-square" alt="MIT License"></a>
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#tieng-viet">Tiếng Việt</a>
</p>

<p align="center">
  <a href="#why-noco-scout">Why</a> ·
  <a href="#product-tour">Product tour</a> ·
  <a href="#how-it-works">How it works</a> ·
  <a href="#quickstart">Quickstart</a> ·
  <a href="#data-trust-and-privacy">Trust</a> ·
  <a href="#development">Development</a>
</p>

<a id="english"></a>

NOCO Scout helps an energy sales team prepare a commercial wall-insulation opportunity before the
first site visit. Enter an address and public data fills in the building facts; NOCO's calculator
turns those facts into savings and incentives; every visible number says where it came from.

The same deterministic engine ranks **300 Buffalo buildings across 11 neighborhoods** on an
interactive 3D map, helping a sales manager decide whom to call first.

> **Built by Team HELIX** for the UB AI for Good Hackathon · NOCO challenge · Buffalo, New York

## Why NOCO Scout

Today, a NOCO rep may visit a building, collect measurements, return to the office, research the
property, and only then prepare an estimate. That makes every opportunity expensive to qualify—and
leaves much of the city unexplored.

NOCO Scout turns that sequence into one traceable flow:

| Start with | Get back |
|---|---|
| One Buffalo address | Building footprint, perimeter, floors, use, source, and confidence |
| Public building geometry | A deterministic wall-insulation estimate based on NOCO's workbook |
| A city-scale dataset | Ranked prospects on an interactive 3D map |
| One qualified building | Customer report, manager report, and CSV export |

## Product tour

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>01 / Address to Quote</h3>
      <p>Search a Buffalo address, inspect its 3D footprint, and review every building fact with its source and confidence.</p>
      <p><strong>Output:</strong> annual energy savings, incentive, net investment, payback, ten-year value, and a printable customer report.</p>
    </td>
    <td width="50%" valign="top">
      <h3>02 / Prospect Map</h3>
      <p>Light up ranked commercial buildings across Buffalo. Hover for sourced facts; click a building for the complete opportunity.</p>
      <p><strong>Output:</strong> filtered prospect list, manager report, and CSV for follow-up.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>03 / Reports that explain themselves</h3>
      <p>Customer-facing estimates stay focused on the upgrade. Internal reports add ranked opportunity data without hiding assumptions.</p>
    </td>
    <td width="50%" valign="top">
      <h3>04 / AI site notes</h3>
      <p>An LLM can structure a synthetic or public site note. It never chooses a formula, threshold, eligibility rule, or final number.</p>
    </td>
  </tr>
</table>

## Feature highlights

- **Address-to-quote:** GIS geometry supplies perimeter, footprint, and floor inputs before a site visit.
- **Buffalo prospecting:** 300 saved commercial buildings make the city-scale experience fast and repeatable.
- **Source on every number:** the interface and reports expose provenance and confidence instead of hiding uncertainty.
- **NOCO-aligned math:** plain Python reproduces the worked calculator example and keeps business rules testable.
- **Offline rehearsal:** the complete demo works from recorded public data with no API key or network call.
- **Two audiences:** one persuasive report for the building owner; one ranked report and CSV for the sales manager.
- **Privacy by construction:** owner names and mailing fields are never requested, stored, or displayed.

## How it works

```text
Buffalo address
   │
   ├── US Census Geocoder ───────── address → coordinates
   ├── OpenStreetMap / Overpass ─── footprint → area, perimeter, floors
   └── Buffalo assessment roll ──── building use and story height
   │
   ▼
BuildingFacts
   every field = value + source + confidence
   │
   ▼
Deterministic insulation calculator
   NOCO workbook formulas + explicit assumptions + incentive rules
   │
   ├── Customer estimate and printable report
   ├── Ranked 3D prospect map
   └── Manager report and CSV
```

The design principle is simple: **the LLM only reads**. Extraction goes in; deterministic rules and
numbers come out.

## Quickstart

### What you need

- Python 3.11 or newer
- `git` and `make`
- macOS or Linux; Windows users can use WSL

### 1. Download and install

```bash
git clone https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD.git
cd AI_FOR_GOOD
make setup
source .venv/bin/activate
```

`make setup` creates a local virtual environment, installs the project, and creates a local `.env`
file from the example when one does not already exist.

### 2. Start with the offline demo

```bash
NOCO_OFFLINE=1 make demo
```

Open [http://localhost:8501](http://localhost:8501), then choose **Address to Quote** or
**Prospect Map**. The offline experience uses saved Buffalo buildings and omits the street basemap.

Good first searches:

```text
33 Franklin St
110 Franklin St
1 Seneca St
532 Main St
107 Delaware Ave
```

### 3. Use live public lookup when you are ready

```bash
make run
```

This enables the street basemap and live lookup for other Buffalo addresses. The **AI site notes**
page can use Anthropic, Groq, or Ollama through local environment settings; `make demo` uses the fake
provider and needs no key.

## Data, trust, and privacy

| Question | NOCO Scout's answer |
|---|---|
| Where did this number come from? | Every visible value carries a source such as OpenStreetMap, Buffalo assessment roll, Census geocoder, NOCO calculator, Assumption, or DEMO value. |
| What happens when a fact is missing? | The app labels the fallback and lowers confidence; it does not silently present a guess as public data. |
| Is project cost known? | No. The demo uses **$8/sq ft**, clearly marked in red and chosen by Team HELIX. Disable it to see “Needs installed cost.” |
| Is NOCO's margin known? | No. The demo uses **35%**, clearly marked illustrative, based on NOCO's stated 30–40% range. |
| Is the current energy supplier known? | No: **“Not in public data: ask the customer.”** The app never guesses. |
| Does the customer report expose internal economics? | No. It never shows NOCO revenue, profit, or margin. |
| Does the assessment data expose owners? | No. Owner names and mailing addresses are never requested, stored, or shown. |

### Public sources

| Data | Source | Terms |
|---|---|---|
| Building outlines and levels | [OpenStreetMap via Overpass](https://www.openstreetmap.org/copyright) | © OpenStreetMap contributors · ODbL 1.0 |
| Building use and story height | [City of Buffalo Final Assessment Roll](https://data.buffalony.gov/d/4t8s-9yih) | City of Buffalo Open Data |
| Address to coordinates | [US Census Geocoder](https://geocoding.geo.census.gov/geocoder/) | Public domain |
| Formulas, constants, and incentive rules | [NOCO Commercial Insulation Savings Calculator v5](docs/NOCO_Commercial_Insulation_Savings_Calculator_v5.xlsx) | Provided by NOCO for the hackathon |

See [the public-data notes](data/public/README.md) for collection, matching, confidence, and licence
details.

## Development

```bash
make test     # network-free test suite; no API key needed
make lint     # Ruff lint and format checks, matching CI
make eval     # labelled extraction cases with the fake provider by default
```

Rebuild the saved Buffalo dataset from its public sources:

```bash
python scripts/prefetch_noco_data.py
```

### Repository map

| Path | Purpose |
|---|---|
| `app/NOCO_Scout.py` | Product home and navigation |
| `app/pages/` | Address to Quote, Prospect Map, and shared UI helpers |
| `src/features/noco_scout/contract.py` | Shared building, calculation, and prospect models |
| `src/features/noco_scout/calc.py` | Deterministic insulation calculator |
| `src/features/noco_scout/geo.py` | Census, OpenStreetMap, Buffalo data, and offline lookup |
| `src/features/noco_scout/prospect.py` | Prospect scoring and illustrative NOCO opportunity |
| `src/features/noco_scout/mapdata.py` | 3D map rows and sourced tooltips |
| `src/features/noco_scout/report.py` | Customer report, manager report, and CSV |
| `data/public/` | Saved public demo data for 300 buildings |
| `src/hackkit/` | Team HELIX's reusable extraction, cache, export, and eval framework |

## Limits and next steps

**Today:** Buffalo only, commercial wall insulation only, illustrative installed cost and margin, and
limited support for landmarks that OpenStreetMap models as several building parts.

**Next:** windows, HVAC, lighting, rooftop solar, more incentive programs, a disadvantaged-community
map layer, utility-bill upload, NOCO CRM integration, and expansion to other cities NOCO serves.

## Team HELIX

| Member | Role |
|---|---|
| [Nguyen-Le-Tuan](https://github.com/Nguyen-Le-Tuan) | Integration, code review, QA, and demo |
| [Anh-08](https://github.com/Anh-08) | GIS pipeline, reports, and UI |
| [phamvotriduc241106](https://github.com/phamvotriduc241106) | Calculator, 3D map, prospect ranking, and AI extraction |
| [NguyenQBao](https://github.com/NguyenQBao) | Research, NOCO liaison, and pitch |

Built with Streamlit and pydeck on top of **hackkit**, Team HELIX's hackathon framework. Code is
available under the [MIT License](LICENSE). Map data © OpenStreetMap contributors.

---

<a id="tieng-viet"></a>

## Tiếng Việt

<p><a href="#english">↑ English</a></p>

**NOCO Scout biến một địa chỉ tại Buffalo thành ước tính nâng cấp cách nhiệt có nguồn dữ liệu rõ
ràng chỉ trong vài giây.** Công cụ lấy hình học tòa nhà từ dữ liệu công khai, chạy công thức của NOCO
bằng mã Python xác định, rồi hiển thị kết quả trên bản đồ 3D và báo cáo tải xuống.

### Sản phẩm có gì?

- **Address to Quote:** nhập địa chỉ, kiểm tra hình khối 3D, dữ kiện, nguồn và độ tin cậy; sau đó tạo
  ước tính và báo cáo cho khách hàng.
- **Prospect Map:** xếp hạng 300 tòa nhà thương mại thuộc 11 khu phố Buffalo; rê chuột để xem dữ liệu
  có nguồn, bấm để mở chi tiết, xuất báo cáo quản lý và CSV.
- **Minh bạch:** mọi con số đều ghi nguồn; chi phí và biên lợi nhuận demo được tô đỏ và ghi rõ là
  minh họa.
- **Riêng tư:** hệ thống không yêu cầu, lưu hay hiển thị tên chủ sở hữu và địa chỉ nhận thư.
- **Chạy offline:** dữ liệu Buffalo đã lưu sẵn giúp trình diễn không cần mạng hoặc API key.

### Chạy thử nhanh

```bash
git clone https://github.com/Nguyen-Le-Tuan/AI_FOR_GOOD.git
cd AI_FOR_GOOD
make setup
source .venv/bin/activate
NOCO_OFFLINE=1 make demo
```

Mở [http://localhost:8501](http://localhost:8501). Để tra cứu dữ liệu công khai trực tiếp, dùng
`make run`. Các con số là **ước tính hỗ trợ bán hàng**, không thay thế khảo sát và báo giá chính thức
của NOCO.
