# Team 2 — Work split

Same content as `work_split.xlsx`.

**What we do:** We study how population size and growth relate to municipal waste, how recycling, incineration and landfilling differ between world regions, and what UN population projections suggest for future waste.

**What we hand in:** 1) GitHub repository with the code. 2) Project report (PDF, about 12–18 pages, English). 3) Presentation (about 14 slides, English).

**Grading:** Data pipeline 30% · Analysis and modelling 30% · Dashboard and visualization 20% · Code quality and teamwork 20%.

**The data:** Two sources that belong together: UNSD waste data (Excel) and UN population data (CSV), both already downloaded. B cleans the waste data, C cleans the population data, A joins them on country code and year. D and E analyse the joined table, F builds the dashboard on it.

**Your package:** 6 packages, about the same work each (12–13 hours). Every package = your code + your section of the report + 2 slides that you present yourself. The Format column says where your code goes; 'Notebook or .py' means you choose.

**How to pick:** Reply in the group chat with the letter you want. First come, first served. Levente has already set up the Git repository and downloaded the data, and is down for A for now, but is happy to swap with anyone.

| Package | Topic | Format | Extra role | Name |
| --- | --- | --- | --- | --- |
| A | Repository, pipeline, joining the data | Notebook or .py | Reviews and merges all pull requests | Birkás Levente |
| B | Cleaning the waste data | Notebook or .py | Report editor |  |
| C | Cleaning the population data, matching countries | Notebook or .py | Presentation coordinator |  |
| D | Data quality, correlation, regression | Notebook | — |  |
| E | Waste-management trends, regions, projection | Notebook | — |  |
| F | Interactive dashboard | Notebook (Plotly) or .py app (Dash or Streamlit) | Live demo in the presentation |  |

**Research question (proposal, decide at the first meeting):** How are population size and growth related to municipal waste, how do recycling, incineration and landfilling differ between world regions, and what do the UN population projections suggest for future waste?

---

## A: Repository, pipeline, joining the data

Join B's waste tables and C's population table into one table with one row per country and year, using the country code (M49) and the year. Add each country's region and the waste per person in kg. List every country that does not match and fix or explain it. Write one script that runs the whole data preparation in order, and a README section that tells anyone how to reproduce the project. Review and merge everyone's pull requests. (Creating the Git repository is already done.)

**Format:** Notebook or .py  
**Report:** data sources and how the pipeline works, with a simple diagram (about 2 pages).  
**Slides:** data sources; pipeline.  
**Extra role:** Reviews and merges all pull requests

---

## B: Cleaning the waste data

Clean the three UNSD waste Excel files: waste collected (2001–2023), recycling percent (2001–2024) and waste treatment shares (latest year per country). Drop the footnote rows at the bottom, turn '...' into missing values, fix the 10 broken country codes in the waste-collected file, and reshape the year columns into one row per country and year. Save three clean CSV files. Push a first rough version early so the others can start. The traps in the files are listed in team2_waste_data/README.md.

**Format:** Notebook or .py  
**Report:** what was wrong in the waste files and how you fixed it (about 1.5 pages).  
**Slides:** research question; problems in the waste data.  
**Extra role:** Report editor: sets up the shared report document, writes the Introduction and Conclusions, makes the style consistent, exports the final PDF

---

## C: Cleaning the population data, matching countries

Clean the UN population files: keep countries only and the Medium variant, 1950–2100, and add the yearly growth rate. Mark which years are projections (after 2023). Build a lookup table that gives every country its sub-region and region. Check that every country in B's waste data has a match in the population data, and list the ones that do not. Save two clean CSV files. Push a first rough version early.

**Format:** Notebook or .py  
**Report:** population data, why we match countries by code and not by name, how regions were assigned (about 1.5 pages).  
**Slides:** population growth by region; country matching.  
**Extra role:** Presentation coordinator: makes the slide template, collects everyone's slides, asks the teacher for the time limit, organises one rehearsal, exports the final deck

---

## D: Data quality, correlation, regression

Check data quality: which years and countries have waste data, and which period is good enough to model. Describe the data with summary statistics and histograms, and decide what to do with outliers. Measure the correlation between population, growth rate and waste. Fit a simple linear regression (waste vs population) and a multiple regression (waste per person vs growth rate, year and region), and explain the results in plain words. Every chart gets a title, units and a short 'what this means' text.

**Format:** Notebook  
**Report:** methods, results and limitations of the analysis (about 3 pages).  
**Slides:** population vs waste chart; regression results in plain words.  

---

## E: Waste-management trends, regions, projection

Compare recycling, incineration and landfilling between world regions (for example a stacked bar chart and box plots). Show how recycling changed from 2001 to 2024 in each region, and how fast. Use the UN population projections to estimate waste in 2030 and 2050 under two simple scenarios: waste per person stays the same, or it keeps its recent trend. Say clearly that this is a scenario, not a forecast. Every chart gets a title, units and a short 'what this means' text.

**Format:** Notebook  
**Report:** results for regions, trends and projections, with limitations (about 3 pages).  
**Slides:** treatment methods by region; projection to 2050.  

---

## F: Interactive dashboard

Build an interactive Plotly dashboard that a non-technical person can explore: a world map of waste per person with a year slider, a country picker that shows waste and population over time, a comparison of treatment methods by region, and the population projection to 2100. Every chart needs a title, units and one sentence that explains it. Use the same colour for each region as D and E. Add 'how to open the dashboard' to the README and test it on a teammate's laptop.

**Format:** Notebook (Plotly) or .py app (Dash or Streamlit)  
**Report:** what the dashboard shows, with 3–4 screenshots (about 1.5 pages).  
**Slides:** 1 dashboard screenshot + a 2-minute live demo.  
**Extra role:** Live demo in the presentation

---

Rules for everybody: work on your own Git branch and open a pull request (never push straight to main) · docstrings and short comments in your code · never edit the raw data by hand · notebooks must run from top to bottom without errors · only the owner edits a notebook.
