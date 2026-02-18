# Space Missions Dashboard

An interactive dashboard for exploring historical space mission data from 1957 onwards, built with Python and Dash.

---

## Setup

**Requirements:** Python 3.8+

```bash
# Clone and enter the repo
git clone <repository-url>
cd Rely-Health-Case-Study

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the dashboard

```bash
python app.py
```

Then open `http://localhost:8050` in your browser.

### Run the tests

```bash
python test_missions.py   # full test suite (91 cases)
python missions.py        # quick function output demo
```

### Project structure

```
.
├── missions.py          # 8 required data functions + helpers
├── test_missions.py     # test suite
├── app.py               # Dash dashboard
├── requirements.txt
└── space_missions.csv   # dataset
```

> The CSV loader also looks for `space_missions (1) 2.csv` and `space_missions (1).csv` as fallbacks, so either filename works.

---

## Why Dash?

I've used Dash in a previous internship and it was the natural pick here. A few reasons:

- **Everything in Python.** No context-switching between JS and Python. Callbacks, layout, and data processing all live in the same file, which keeps a small project like this easy to follow.
- **Plotly out of the box.** Dash renders Plotly charts natively, so there's no glue code needed between the charting library and the UI framework.
- **Interactivity without JavaScript.** Dropdowns, sliders, multi-selects, and reactive callbacks are first-class citizens. Building the same filter bar in Flask + vanilla JS would have taken considerably longer.
- **Lightweight footprint.** There's no build step, no bundler, no separate frontend server. `python app.py` is all you need.
- **DataTable component.** `dash_table.DataTable` gives you server-side sorting, filtering, and pagination for free — exactly what the spec asked for.

---

## Dashboard visualizations

### 1. Launches per Year — Area line chart

A line chart with an area fill showing mission volume year over year. A line was the right choice here because the primary question is "how has launch frequency changed over time?" — trend and direction matter more than individual point comparisons. The area fill adds a sense of magnitude without cluttering the chart. A bar chart would have worked too, but becomes cramped for 60+ years of annual data.

### 2. Mission Status Distribution — Donut chart

A donut breaks down the four outcome categories (Success, Failure, Partial Failure, Prelaunch Failure) as proportions of the whole. The hole in the centre is used to show the total mission count in context. A pie chart would carry the same information, but a donut is cleaner at small sizes because the centre gives you somewhere to anchor a summary number. Each slice is colour-coded semantically: green for success, red for failure, amber for partial, purple for prelaunch.

### 3. Top 15 Companies by Mission Count — Horizontal bar chart

Horizontal bars are the standard choice when you have long category labels (company names) and want to rank them. Vertical bars would truncate or rotate the labels. The gradient fill (muted blue → bright blue) gives a secondary visual cue on top of bar length, making the rank ordering read faster.

### 4. Success Rate by Top 15 Companies — Horizontal bar chart with diverging colour scale

Same orientation rationale as above, but the colour scale here does more work: it runs from red (low success rate) through amber to green (high), mirroring traffic-light intuition. This lets you scan across companies and spot outliers immediately, without reading exact values. The x-axis is fixed at 0–100 so bars are always comparable even when the filter changes the visible companies.

### 5. Launch Activity Heatmap — Year × Decade grid

The heatmap answers "which decade, and which year within that decade, saw the most launches?" A grid encodes two categorical dimensions (decade, year-within-decade) against a continuous one (count), which is exactly what heatmaps are built for. It also surfaces gaps and clusters — the cold-war surge, the post-Soviet dip, the recent commercial boom — at a glance, in a way that a grouped bar chart would struggle to show cleanly. The colour scale runs from a dark navy (zero/low) to the dashboard's accent blue (peak) so empty cells are visually distinct from the background.

---

## Functions (`missions.py`)

All eight required functions are implemented in `missions.py`. Data is loaded once at startup, cached, and a defensive copy is returned to prevent external mutation.

| Function | Signature | Returns |
|---|---|---|
| `getMissionCountByCompany` | `(companyName: str) -> int` | Total missions for a company |
| `getSuccessRate` | `(companyName: str) -> float` | Success % rounded to 2 dp |
| `getMissionsByDateRange` | `(startDate: str, endDate: str) -> list` | Mission names sorted chronologically |
| `getTopCompaniesByMissionCount` | `(n: int) -> list` | `[(name, count), ...]` top N companies |
| `getMissionStatusCount` | `() -> dict` | Count per status, all four keys always present |
| `getMissionsByYear` | `(year: int) -> int` | Mission count for a given year |
| `getMostUsedRocket` | `() -> str` | Most flown rocket, alphabetical tie-break |
| `getAverageMissionsPerYear` | `(startYear: int, endYear: int) -> float` | Average per year, rounded to 2 dp |

All functions validate their inputs strictly and raise `TypeError` or `ValueError` with descriptive messages for bad inputs (wrong types, `None`, booleans passed as ints, out-of-range years, malformed date strings, etc.).

Dates must be passed in strict `YYYY-MM-DD` format. Ambiguous formats (`01-02-03`, `01/01/2020`), partial strings (`"2020"`), and timezone-aware strings (`"2020-01-01Z"`) are all rejected to prevent silent wrong-date bugs.

---

## Tests (`test_missions.py`)

The test suite covers 91 cases across all eight functions: normal inputs, boundary conditions, unknown/empty values, and invalid inputs.

