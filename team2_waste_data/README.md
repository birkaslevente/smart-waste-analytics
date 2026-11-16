# Team 2 — raw data pack

Smart Waste Analytics & Demographics: municipal waste generation and treatment versus historical population growth and future projections.

Downloaded on **16 November 2026** (Europe/Budapest, CET, UTC+1) onto this machine. Official file timestamps (HTTP `Last-Modified`, UTC) are listed under each file.

Re-download everything with:

```bash
pip install -r requirements.txt
python scripts/download_data.py
```

To try the UN Population Data Portal API as well (optional):

```bash
# Request a free token at https://population.un.org/dataportalapi/token/index.html
TOKEN="your-token" python scripts/download_data.py
```

The script always also saves the official WPP 2024 bulk CSVs, which do not need a token.

---

## 1. UNSD Environmental Indicators — Waste

Course URL: <https://unstats.un.org/unsd/environment/qindicators.htm> (redirects to the current page <https://unstats.un.org/unsd/envstats/qindicators>).

Original Excel matrices are stored untouched in `raw/unsd/`. Each workbook has a `Description` (or `description`) sheet with definitions, and a `Data` (or `data`) sheet with the numbers. A snapshot of the landing page is in `sources/unsd_qindicators_page.html`.

There is **no published “Municipal waste generated” time-series matrix** on the current indicators page. The closest official generation-side series is **Municipal waste collected**. In the UNSD/UNEP questionnaire, “generated” = waste collected plus an estimate of waste from areas not served by collection. Treatment (recycling, composting, incineration, landfilling) is published as a **latest-year snapshot**, except the recycling share, which is a 2001–2024 time series.

Country identifier: `CountryID` is the UN **M49** numeric code (same as WPP `LocID` and the Data Portal API `locations.id`). There is **no ISO3 column** in the UNSD files — join to population data on M49, or on country name as a fallback.

Missing values appear as `...` or `…`. The `Source` column (where present) is typically `U` = UNSD/UNEP questionnaire, `E` = Eurostat, `O` = OECD. Definitions and estimation methods can differ across countries; use the footnote columns.

`pandas` shapes below include footnote/legend rows at the bottom of the Data sheet (where `CountryID` is a letter code or the text “Footnote number”). Drop those before analysis.

### `raw/unsd/Municipal waste collected.xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal%20waste%20collected.xlsx>
- HTTP Last-Modified: 9 January 2026, 20:20:30 UTC. Description sheet “Date of release”: 17 December 2025. Official coverage: 143 countries.
- Time series, **2001–2023**. Unit: thousand tonnes (1000 tonnes).
- Columns: `CountryID`, `Country`, `Source`, year columns 2001–2023, then `Footnotes 2001` … `Footnotes 2023`.
- pandas Data sheet: shape `(217, 50)`.
- **Caveat:** 10 OECD-source rows still have an unresolved Excel formula in `CountryID` (`=VLOOKUP(...)`) instead of an M49 code. pandas will not see a numeric ID for: Argentina (M49 **32**), Australia (**36**), Chile (**152**), Colombia (**170**), Costa Rica (**188**), Israel (**376**), Japan (**392**), Mexico (**484**), New Zealand (**554**), Saudi Arabia (**682**). Fill these from the name or from `raw/unpop/unpop_api_locations.json` / the WPP file. Data values in the year columns are present.

### `raw/unsd/Municipal waste collection (latest year).xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2022/Tables/Municipal%20waste%20collection%20(latest%20year).xlsx>
- HTTP Last-Modified: 27 March 2024, 17:45:05 UTC. Date of release: 19 March 2024 (Questionnaire 2022 tables — older than the 2024 time series above). Official coverage: 144 countries.
- Latest year snapshot. Units: thousand tonnes, percent, or kg as indicated in row 2.
- Columns: `CountryID`, `Country`, `Source`, `Latest year available`, `Municipal waste collected`, `Total population served by municipal waste collection`, `Municipal waste collected per capita served`, plus footnotes.
- pandas Data sheet: shape `(185, 9)`.

### `raw/unsd/Municipal waste treatment (latest year).xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal%20waste%20treatment%20(latest%20year).xlsx>
- HTTP Last-Modified: 27 April 2026, 15:11:50 UTC. Date of release: 9 April 2026. Official coverage: 106 countries and areas. OECD/Eurostat extracted 9 April 2026.
- Latest year snapshot (year differs by country). Units: thousand tonnes for waste managed; **percent** for treatment shares.
- Columns: `CountryID`, `Country`, `Source`, `Year`, Municipal waste managed (1000 tonnes), Municipal waste **landfilled**, **incinerated**, **recycled**, **composted**, managed with **other** treatment or disposal (all shares in %), plus footnote columns.
- pandas Data sheet: shape `(155, 16)`.
- This is the main management/treatment matrix. It is **not** a time series.

### `raw/unsd/Percentage of municipal waste collected which is recycled.xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Percentage%20of%20municipal%20waste%20collected%20which%20is%20recycled.xlsx>
- HTTP Last-Modified: 6 May 2026, 12:49:32 UTC. Date of release: 24 April 2026. Official coverage: 105 countries and areas.
- Time series, **2001–2024**. Unit: percent. Calculated by UNSD from Eurostat, OECD or UNSD sources.
- Columns: `CountryID`, `Country`, `Source`, year columns 2001–2024, footnote columns.
- pandas Data sheet: shape `(162, 52)`.

### `raw/unsd/Total population served by municipal waste collection.xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Total%20population%20served%20by%20municipal%20waste%20collection.xlsx>
- HTTP Last-Modified: 9 January 2026, 20:20:30 UTC. Date of release: 17 December 2025. Official coverage: 78 countries.
- Time series, **2001–2024**. Unit: percent of total resident population served by regular municipal collection.
- pandas Data sheet: shape `(102, 51)`.

### `raw/unsd/Composition municipal waste (latest year).xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Composition%20municipal%20waste%20(latest%20year).xlsx>
- HTTP Last-Modified: 27 April 2026, 15:11:50 UTC. Date of release: 2 April 2026. Official coverage: 95 countries and areas.
- Latest year snapshot. Unit: percent (paper, textiles, plastics, glass, metals, other inorganic, organic, plus footnotes).
- pandas Data sheet: shape `(149, 17)`.

### `raw/unsd/Municipal waste collection at city level in selected cities (latest year).xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal%20waste%20collection%20at%20city%20level%20in%20selected%20cities%20(latest%20year).xlsx>
- HTTP Last-Modified: 27 April 2026, 15:11:50 UTC. Date of release: 9 April 2026. Official coverage: 229 cities in 87 countries (the Description sheet typo says “countires”).
- Latest year, city-level collected amounts, city population, population served, kg per capita served. Some per-capita cells are still Excel formulas; open with data_only or recompute from the tonne and population columns.
- pandas Data sheet: shape `(254, 11)`.

### `raw/unsd/Municipal waste treatment at city level in selected cities.xlsx`

- Source URL: <https://unstats.un.org/unsd/envstats/Questionnaires/2024/Tables/Municipal%20waste%20treatment%20at%20city%20level%20in%20selected%20cities.xlsx>
- HTTP Last-Modified: 27 April 2026, 15:11:50 UTC. Date of release: 10 April 2026. Official coverage: 151 cities in 59 countries.
- Latest year, city-level collected tonnes and treatment shares (recycled, composted, incinerated, landfilled, other).
- pandas Data sheet: shape `(186, 16)`.

Hazardous-waste and e-waste indicator tables exist on the same page but were not downloaded; they are outside the municipal-waste brief.

---

## 2. UN Population Division

### API status (checked 16 November 2026)

- Guide: <https://population.un.org/dataportal/about/dataapi>
- Base URL: `https://population.un.org/dataportalapi/api/v1`
- **Metadata works without a token:** `GET /indicators`, `/locations`, `/topics`, `/sources` all returned HTTP 200.
- **Data endpoints require a free bearer token.** `GET /data/indicators/49/locations/348?startYear=1990&endYear=1992` returned **HTTP 401**, `WWW-Authenticate: Bearer`, empty body. HEAD requests to data and metadata URLs often return 405 (`Allow: GET`) — use GET.
- Request a token (free form, sent by email): <https://population.un.org/dataportalapi/token/index.html>
- Call format once you have a token:

```text
Authorization: Bearer <TOKEN>
GET https://population.un.org/dataportalapi/api/v1/data/indicators/49/locations/{m49ids}?startYear=1950&endYear=2100&variants=4&sexes=3&format=csv
```

- Indicator **49** = Total population by sex (mid-year, persons), source World Population Prospects, 1950–2100. API `defaultVariantId=4`, `defaultSexId=3` (both sexes).
- **Important:** API variant IDs are not the same as WPP `VarID`. In the official WPP CSV, Medium is `VarID == 2` / `Variant == "Medium"`. After an API pull, filter on the variant *name*, not by assuming API `4` equals WPP `VarID` 4 (that WPP code is “Low”).
- Location IDs in the API are M49 codes and include ISO2/ISO3. 300 locations were returned (countries plus regions/aggregates). The `/variants` and `/sexes` collection endpoints currently return 404.
- `scripts/download_data.py` will pull indicator 49 as CSV into `raw/unpop/unpop_api_total_population.csv` when `TOKEN` (or `UNPOP_TOKEN` / `UN_API_TOKEN`) is set. Without a token it records the 401 and uses the WPP bulk files below.

### Fallback: official WPP 2024 bulk CSV

The WPP 2026 revision has been postponed to 11 July 2027, so **WPP 2024** is still the current official revision. Downloads page (SPA): <https://population.un.org/wpp/>. Older `/wpp/downloads` paths 404; the working file base is:

`https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/`

An interim update of 19 January 2026 revises **Togo only** (medium estimates 1950–2023 and medium projections 2024–2100). Other countries and all global/regional aggregates are unchanged. The update zip named in that release note (`WPP2024_CSV_files_update.zip`) was not found at the documented `.../wpp/assets/Files/` path at download time, so the files below are the standard 13 December 2024 release. See `raw/unpop/WPP2024_Release-Note-rev1.pdf`.

Population figures in these CSVs are in **thousands of persons** unless a column says otherwise (for example rates). Files are UTF-8 with BOM.

### `raw/unpop/WPP2024_TotalPopulationBySex.csv.gz` (official original) and `.csv` (decompressed)

- Source URL: <https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_TotalPopulationBySex.csv.gz>
- HTTP Last-Modified: 13 December 2024, 19:11:28 UTC. Size of `.gz`: 16,980,593 bytes.
- Mid-year population by sex, **1950–2100**, all published variants.
- Columns: `SortOrder`, `LocID` (M49), `Notes`, `ISO3_code`, `ISO2_code`, `SDMX_code`, `LocTypeID`, `LocTypeName`, `ParentID`, `Location`, `VarID`, `Variant`, `Time`, `MidPeriod`, `PopMale`, `PopFemale`, `PopTotal`, `PopDensity`.
- pandas: shape `(720210, 18)`.
- **237 countries/areas** (`LocTypeID == 4`), all with ISO3. Also world, regions, SDG regions, income groups, and other aggregates (`ISO3_code` is often empty for aggregates).
- Use **`Variant == "Medium"`** (VarID 2) for the medium variant. For countries this series runs **1950–2100** in a single variant label (historical estimates and projections together). Other variants (High, Low, Zero migration, prediction intervals, …) cover 2024–2100 only.
- `PopTotal` / `PopMale` / `PopFemale` are in thousands; `PopDensity` is persons per km².

### `raw/unpop/WPP2024_Demographic_Indicators_Medium.csv.gz` and `.csv`

- Source URL: <https://population.un.org/wpp/assets/Excel%20Files/1_Indicator%20(Standard)/CSV_FILES/WPP2024_Demographic_Indicators_Medium.csv.gz>
- HTTP Last-Modified: 13 December 2024, 19:11:17 UTC. Size of `.gz`: 16,557,272 bytes.
- Medium variant only. Years in the file: **1950–2101** (some 1 January indicators include 2101; mid-year population runs through 2100). 237 countries/areas plus aggregates (555 location codes).
- 67 columns, including `TPopulation1July`, `PopGrowthRate`, `PopChange`, `Births`, `Deaths`, `TFR`, `LEx`, `NetMigrations`, and standard location/ISO/M49 identifiers.
- pandas: shape `(84360, 67)`.
- Useful for correlating waste with **population growth rates**, not only stock population.

### API metadata (no token required)

- `raw/unpop/unpop_api_locations.json` — 300 locations with `id` (M49), `name`, `iso3`, `iso2`. Convenient lookup table for joining UNSD `CountryID` to ISO3.
- `raw/unpop/unpop_api_indicators.json` — 86 indicators (includes 49 = Total population by sex).
- `raw/unpop/api_topics.json`, `raw/unpop/api_sources.json` — topic and source catalogues.

### `raw/unpop/WPP2024_Release-Note-rev1.pdf`

- Source URL: <https://population.un.org/wpp/assets/Files/WPP2024_Release-Note-rev1.pdf>
- HTTP Last-Modified: 10 February 2026, 19:12:30 UTC. Documents the 19 January 2026 Togo interim update and the postponement of the next WPP revision to 11 July 2027.

---

## 3. Matching countries

Recommended key: **M49 numeric code**.

| Dataset | Country code columns |
| --- | --- |
| UNSD waste Excel | `CountryID` (M49). No ISO3. Watch the 10 missing IDs in `Municipal waste collected.xlsx`. |
| WPP CSVs | `LocID` (M49), `ISO3_code`, `ISO2_code`, `SDMX_code`. Filter `LocTypeID == 4` for countries/areas. |
| Data Portal API | `locations.id` (M49), `iso3`, `iso2`. |

Country names are not a safe primary key (punctuation, “Bolivia (Plurinational State of)”, etc.).

---

## 4. Quick sanity check (pandas, this download)

Run `python scripts/download_data.py` (it reprints these) or:

```python
import json
from pathlib import Path
import pandas as pd

root = Path("raw")
for p in sorted((root / "unsd").glob("*.xlsx")):
    xl = pd.ExcelFile(p)
    sheet = next(s for s in xl.sheet_names if s.lower() == "data")
    df = pd.read_excel(p, sheet_name=sheet)
    print(p.name, df.shape, list(df.columns)[:8], "...")

for name in [
    "WPP2024_TotalPopulationBySex.csv",
    "WPP2024_Demographic_Indicators_Medium.csv",
]:
    p = root / "unpop" / name
    df = pd.read_csv(p, encoding="utf-8-sig")
    print(name, df.shape, list(df.columns))
```

Observed on 16 November 2026:

| File | shape |
| --- | --- |
| Municipal waste collected.xlsx (Data) | (217, 50) |
| Municipal waste collection (latest year).xlsx (Data) | (185, 9) |
| Municipal waste treatment (latest year).xlsx (Data) | (155, 16) |
| Percentage of municipal waste collected which is recycled.xlsx (Data) | (162, 52) |
| Total population served by municipal waste collection.xlsx (Data) | (102, 51) |
| Composition municipal waste (latest year).xlsx (data) | (149, 17) |
| Municipal waste collection at city level … (data) | (254, 11) |
| Municipal waste treatment at city level … (data) | (186, 16) |
| WPP2024_TotalPopulationBySex.csv | (720210, 18) |
| WPP2024_Demographic_Indicators_Medium.csv | (84360, 67) |
| unpop_api_locations.json | 300 records |
| unpop_api_indicators.json | 86 records |

---

## 5. Layout

```
team2_waste_data/
  README.md
  requirements.txt
  scripts/download_data.py
  raw/unsd/          # untouched official UNSD Excel matrices
  raw/unpop/         # WPP CSVs (gz + decompressed), API metadata, release note
  sources/           # snapshot of the UNSD indicators landing page
```
