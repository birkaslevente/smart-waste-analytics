# Team 2 — Smart Waste Analytics & Demographics

Separate repository for the teamwork project. The individual project lives in `../individual-project/` and is not part of this repo.

Team members:

- Boakye Anthony
- Bouattour Rayen
- Birkás Levente
- Elkerch Mohamed Amine
- Islam Md Shajedul
- Yusupov Abbosbek

## Objective

Investigate how waste generation and waste-management patterns relate to population development.

Indicators to model:

- Municipal waste generation
- Recycling
- Incineration
- Landfilling
- Historical population growth
- Future demographic projections

## Deliverables

- Shared GitHub repository. Birkás Levente creates it, uploads this folder, and invites the team.
- Project report
- Presentation

## Data sources

| Source | What to use |
| --- | --- |
| UNSD Environmental Indicators, Waste Data | Raw matrices for waste Generation and Management |
| UN Population Division Data Portal | Demographic data via the UN Population API Guide, retrieved programmatically as JSON or CSV |

For every dataset, record the source, indicators, countries or regions, time period, and units.

## Technical requirements

- Script ingestion and transformation in Python.
- Use Pandas, NumPy, or similar tools where appropriate.
- Do not use manual Excel edits as the main transformation method.
- Match differing country names and country codes in code.
- Make the project reproducible from the code plus raw-data instructions.
- Keep a clean commit history and use Git branches.
- Document code with comments and docstrings.

## Research questions to choose from

- How does population growth affect municipal waste generation?
- Which waste-management methods are becoming more common?
- Are population projections associated with future increases in waste?
- Do recycling, incineration, or landfilling patterns differ between regions?

Pick and write down the exact question before modelling.

## Pipeline

1. **Collection** — download or retrieve raw waste and demographic data.
2. **Cleaning and integration** — missing values, duplicates, standardized country names, matched country codes, aligned years, converted types and units.
3. **Analysis** — trends, regional comparisons, correlation, regression, and forecasting only where the data supports it.
4. **Visualization** — time series, regional comparisons, maps, stacked management-method charts, and an interactive dashboard with labels a non-technical reader can follow.
5. **Conclusions** — findings, country or region differences, the population–waste relationship, limitations, and implications for waste management.

## Grading

| Area | Weight |
| --- | --- |
| Data engineering and pipeline | 30% |
| Analytical depth and modelling | 30% |
| Dashboard and visualization | 20% |
| Code quality and collaboration | 20% |

## Suggested layout

```
team-smart-waste/
  README.md
  data/raw/            original downloads, unchanged
  data/processed/      script outputs
  notebooks/           analysis and modelling
  src/                 ingestion, cleaning, merge
  dashboard/           interactive dashboard
  outputs/             figures, tables, dashboard
  report/              project report
  presentation/        slides
```

## Who does what

The split is in `WORK_SPLIT.md`: six packages (A–F), one per person, each with code, a report section, and 2 slides. Write your name next to a letter. The downloaded files stay in `team2_waste_data/raw/`. Do not edit those files by hand.
