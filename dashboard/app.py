"""Smart Waste Analytics - interactive dashboard (package F).

Run from the repository root, after `python run_pipeline.py` has created the tables:
    pip install -r requirements.txt
    pip install -r dashboard/requirements.txt
    streamlit run dashboard/app.py

Reads three tables from team2_waste_data/processed/:
    panel_country_year.csv       one row per country and year, with waste per person (A)
    population_clean.csv         population 1950-2100 with a projection flag (C)
    treatment_latest_joined.csv  treatment shares, latest year per country (A)
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).resolve().parents[1] / "team2_waste_data" / "processed"

# MUST be identical to the colours used by D and E (best: one shared dict imported by all three).
REGION_COLOURS = {
    "Africa": "#E69F00",
    "Americas": "#D55E00",
    "Asia": "#56B4E9",
    "Europe": "#009E73",
    "Oceania": "#CC79A7",
}
# Treatment columns in treatment_latest_joined.csv -> label shown to the user, plus their own colours
METHODS = {
    "Recycled_Pct": ("Recycled", "#2A9D8F"),
    "Composted_Pct": ("Composted", "#8AB17D"),
    "Incinerated_Pct": ("Incinerated", "#E76F51"),
    "Landfilled_Pct": ("Landfilled", "#6D597A"),
    "Other_Pct": ("Other", "#B8B8B8"),
}

st.set_page_config(page_title="Smart Waste Analytics", layout="wide")


@st.cache_data
def load():
    """Read the three prepared tables and attach each country's region to the population table."""
    panel = pd.read_csv(DATA / "panel_country_year.csv")
    pop = pd.read_csv(DATA / "population_clean.csv")
    treat = pd.read_csv(DATA / "treatment_latest_joined.csv")
    regions = pd.read_csv(DATA / "country_region_lookup.csv")[["CountryID", "Region"]]
    pop = pop.merge(regions, on="CountryID", how="inner", validate="m:1")
    return panel, pop, treat


panel, pop, treat = load()
waste = panel.dropna(subset=["Waste_kg_per_capita"])
last_observed = int(pop.loc[~pop.Is_Projection, "Year"].max())

st.title("Waste and population around the world")
st.caption("Sources: UN waste statistics (municipal waste) and UN World Population Prospects 2024. "
           "Grey or missing values mean the country did not report that year.")

# 1 ---- World map with year slider
st.header("1. Waste per person around the world")
years = sorted(waste.Year.unique())
best_year = int(waste.groupby("Year").size().idxmax())          # year with the most reporting countries
year = st.select_slider("Choose a year", options=years, value=best_year)
d = waste[waste.Year == year]
fig = px.choropleth(
    d, locations="ISO3", color="Waste_kg_per_capita", hover_name="Country",
    hover_data={"ISO3": False, "Waste_kg_per_capita": ":.0f"},
    color_continuous_scale="YlOrRd", range_color=(0, waste.Waste_kg_per_capita.quantile(0.98)),
    labels={"Waste_kg_per_capita": "kg per person"},
    title=f"Municipal waste collected per person, {year} (kg per person per year)")
fig.update_geos(projection_type="natural earth", showframe=False, lataxis_range=[-58, 85])
fig.update_layout(height=620, margin=dict(l=0, r=0, t=50, b=0))
st.plotly_chart(fig, width="stretch")
st.caption(f"Darker countries collect more waste per person; {len(d)} countries reported in {year}, "
           "the rest are grey. Colours stop at the 98th percentile so a few extreme values do not hide the rest.")

# 2 ---- Country picker
st.header("2. One country over time")
countries = sorted(waste.Country.unique())
country = st.selectbox("Choose a country", countries,
                       index=countries.index("Germany") if "Germany" in countries else 0)
cw = waste[waste.Country == country].sort_values("Year")
cp = pop[(pop.Country == country) & ~pop.Is_Projection].sort_values("Year")
left, right = st.columns(2)
left.plotly_chart(px.line(cw, x="Year", y="Waste_kg_per_capita", markers=True,
                          labels={"Waste_kg_per_capita": "kg per person"},
                          title=f"{country}: waste per person (kg per person per year)"),
                  width="stretch")
right.plotly_chart(px.line(cp.assign(People_millions=cp.Population_1000 / 1000), x="Year",
                           y="People_millions", markers=True, labels={"People_millions": "Million people"},
                           title=f"{country}: population (million people)"),
                   width="stretch")
st.caption("Compare the two lines: does waste per person change when the population changes?")

# 3 ---- Treatment methods by region (only countries whose shares add up to about 100%)
st.header("3. How each region treats its waste")
ok = treat[(treat.Shares_Quality == "complete") & treat.Managed_1000t.gt(0)]
rows = []
for region, g in ok.groupby("Region"):
    for col, (label, _) in METHODS.items():
        rows.append({"Region": f"{region} ({len(g)} countries)", "Method": label,
                     "Share": (g[col] * g.Managed_1000t).sum() / g.Managed_1000t.sum()})
m = pd.DataFrame(rows)
st.plotly_chart(
    px.bar(m, x="Region", y="Share", color="Method", barmode="stack",
           color_discrete_map={label: colour for label, colour in METHODS.values()},
           category_orders={"Method": [label for label, _ in METHODS.values()]},
           labels={"Share": "Share of managed waste (%)"},
           title="Waste treatment by region, latest year reported (% of managed waste)"),
    width="stretch")
st.caption("Only countries whose treatment shares add up to about 100% are included; "
           "bigger countries count for more, and the latest reporting year differs by country.")

# 4 ---- Population projection to 2100
st.header("4. Population until 2100")
all_regions = sorted(pop.Region.unique())
chosen = st.multiselect("Regions", all_regions, default=all_regions)
p = (pop[pop.Region.isin(chosen)].groupby(["Region", "Year", "Is_Projection"], as_index=False)
     .Population_1000.sum())
p["Millions"] = p.Population_1000 / 1000
fig = go.Figure()
for region in chosen:
    r = p[p.Region == region].sort_values("Year")
    colour = REGION_COLOURS.get(region)
    fig.add_trace(go.Scatter(x=r[~r.Is_Projection].Year, y=r[~r.Is_Projection].Millions, mode="lines",
                             name=region, legendgroup=region, line=dict(color=colour)))
    proj = r[r.Year >= last_observed]                          # starts at the last observed year: no gap
    fig.add_trace(go.Scatter(x=proj.Year, y=proj.Millions, mode="lines", name=f"{region} (projection)",
                             legendgroup=region, showlegend=False, line=dict(color=colour, dash="dash")))
fig.update_layout(title="Population by region, 1950-2100 (million people; dashed = UN projection)",
                  xaxis_title="Year", yaxis_title="Million people")
st.plotly_chart(fig, width="stretch")
st.caption(f"Solid lines are measured up to {last_observed}; dashed lines are the UN Medium projection, not measured data.")
