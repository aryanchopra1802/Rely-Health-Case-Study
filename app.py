import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, dash_table, Input, Output
import dash  # noqa: F401

from missions import (
    _load_data,
    getMissionStatusCount,
    getMostUsedRocket,
    getTopCompaniesByMissionCount,
)

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Space Missions Dashboard"

df = _load_data()

all_companies       = sorted(df["Company"].dropna().unique().tolist())
all_statuses        = sorted(df["MissionStatus"].dropna().unique().tolist())
all_rocket_statuses = sorted(df["RocketStatus"].dropna().unique().tolist())

_valid_years = df["Year"].dropna()
min_year = int(_valid_years.min()) if not _valid_years.empty else 1957
max_year = int(_valid_years.max()) if not _valid_years.empty else 2022

COLORS = {
    "bg":        "#0d1117",
    "panel":     "#161b22",
    "border":    "#30363d",
    "accent1":   "#58a6ff",
    "accent2":   "#8b949e",
    "accent3":   "#c9d1d9",
    "success":   "#3fb950",
    "failure":   "#f85149",
    "partial":   "#d29922",
    "prelaunch": "#bc8cff",
    "text":      "#e6edf3",
    "muted":     "#8b949e",
}

STATUS_COLORS = {
    "Success":           COLORS["success"],
    "Failure":           COLORS["failure"],
    "Partial Failure":   COLORS["partial"],
    "Prelaunch Failure": COLORS["prelaunch"],
}


def base_layout(**overrides):
    """Returns the base dark-theme layout dict, deep-merging any per-chart overrides."""
    xaxis  = {"gridcolor": COLORS["border"], "linecolor": COLORS["border"], "zerolinecolor": COLORS["border"]}
    yaxis  = {"gridcolor": COLORS["border"], "linecolor": COLORS["border"], "zerolinecolor": COLORS["border"]}
    legend = {"bgcolor": "rgba(0,0,0,0)", "bordercolor": COLORS["border"]}

    if "xaxis" in overrides:
        xaxis.update(overrides.pop("xaxis"))
    if "yaxis" in overrides:
        yaxis.update(overrides.pop("yaxis"))
    if "legend" in overrides:
        legend.update(overrides.pop("legend"))

    layout = dict(
        paper_bgcolor=COLORS["panel"],
        plot_bgcolor=COLORS["bg"],
        font=dict(color=COLORS["text"], family="Inter, Arial, sans-serif"),
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=xaxis,
        yaxis=yaxis,
        legend=legend,
    )
    layout.update(overrides)
    return layout


def kpi_card(title, value, subtitle="", accent=COLORS["accent1"]):
    return html.Div(
        style={
            "background": COLORS["panel"],
            "border": f"1px solid {COLORS['border']}",
            "borderTop": f"3px solid {accent}",
            "borderRadius": "8px",
            "padding": "20px 24px",
            "flex": "1",
            "minWidth": "160px",
        },
        children=[
            html.P(title, style={"margin": "0 0 6px 0", "fontSize": "12px", "color": COLORS["muted"], "textTransform": "uppercase", "letterSpacing": "1px"}),
            html.H2(value, style={"margin": "0 0 4px 0", "fontSize": "28px", "fontWeight": "700", "color": accent}),
            html.P(subtitle, style={"margin": "0", "fontSize": "12px", "color": COLORS["muted"]}),
        ],
    )


def section_title(text):
    return html.H3(text, style={"color": COLORS["accent1"], "fontSize": "17px", "letterSpacing": "2px",
                                 "textTransform": "uppercase", "marginBottom": "16px", "marginTop": "0"})


def color_legend(items):
    """Renders a row of colored dot + label pairs. items = [(color, label), ...]"""
    chips = []
    for color, label in items:
        chips.append(html.Span(style={
            "display": "inline-block", "width": "10px", "height": "10px",
            "borderRadius": "50%", "backgroundColor": color,
            "marginRight": "5px", "flexShrink": "0",
        }))
        chips.append(html.Span(label, style={
            "fontSize": "11px", "color": COLORS["muted"], "marginRight": "14px",
        }))
    return html.Div(chips, style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "marginBottom": "10px"})


status_totals = getMissionStatusCount()
total_missions = sum(status_totals.values())
global_success_rate = round(status_totals["Success"] / total_missions * 100, 2) if total_missions else 0
most_used_rocket = getMostUsedRocket()
top_company = getTopCompaniesByMissionCount(1)[0][0]

app.layout = html.Div(
    style={"background": COLORS["bg"], "minHeight": "100vh", "fontFamily": "Inter, Arial, sans-serif", "color": COLORS["text"]},
    children=[

        html.Div(
            style={
                "background": COLORS["panel"],
                "borderBottom": f"1px solid {COLORS['border']}",
                "padding": "16px 40px",
                "textAlign": "center",
            },
            children=[
                html.H1("Space Missions Dashboard", style={"margin": "0", "fontSize": "20px", "fontWeight": "600", "color": COLORS["text"]}),
            ],
        ),

        html.Div(
            style={"padding": "32px 40px", "maxWidth": "1600px", "margin": "0 auto"},
            children=[

                html.Div(
                    style={
                        "background": COLORS["panel"],
                        "border": f"1px solid {COLORS['border']}",
                        "borderRadius": "8px",
                        "padding": "20px 24px",
                        "marginBottom": "24px",
                    },
                    children=[
                        section_title("Filters"),
                        html.Div(
                            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "alignItems": "flex-end"},
                            children=[
                                html.Div(style={"flex": "2", "minWidth": "280px"}, children=[
                                    html.Label("Year Range", style={"fontSize": "14px", "color": COLORS["muted"], "marginBottom": "8px", "display": "block"}),
                                    dcc.RangeSlider(
                                        id="year-slider",
                                        min=min_year, max=max_year,
                                        value=[min_year, max_year],
                                        marks={y: {"label": str(y), "style": {"color": COLORS["muted"], "fontSize": "10px"}}
                                               for y in range(min_year, max_year + 1, 10)},
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    ),
                                ]),

                                html.Div(style={"flex": "2", "minWidth": "240px"}, children=[
                                    html.Label("Company", style={"fontSize": "14px", "color": COLORS["muted"], "marginBottom": "8px", "display": "block"}),
                                    dcc.Dropdown(
                                        id="company-filter",
                                        options=[{"label": c, "value": c} for c in all_companies],
                                        value=[],
                                        multi=True,
                                        placeholder="All companies…",
                                        style={"fontSize": "13px"},
                                    ),
                                ]),

                                html.Div(style={"flex": "1", "minWidth": "200px"}, children=[
                                    html.Label("Mission Status", style={"fontSize": "14px", "color": COLORS["muted"], "marginBottom": "8px", "display": "block"}),
                                    dcc.Dropdown(
                                        id="status-filter",
                                        options=[{"label": s, "value": s} for s in all_statuses],
                                        value=[],
                                        multi=True,
                                        placeholder="All statuses…",
                                        style={"fontSize": "13px"},
                                    ),
                                ]),

                                html.Div(style={"flex": "1", "minWidth": "180px"}, children=[
                                    html.Label("Rocket Status", style={"fontSize": "14px", "color": COLORS["muted"], "marginBottom": "8px", "display": "block"}),
                                    dcc.Dropdown(
                                        id="rocket-status-filter",
                                        options=[{"label": s, "value": s} for s in all_rocket_statuses],
                                        value=[],
                                        multi=True,
                                        placeholder="All…",
                                        style={"fontSize": "13px"},
                                    ),
                                ]),

                                html.Button(
                                    "Reset Filters",
                                    id="reset-btn",
                                    n_clicks=0,
                                    style={
                                        "background": "transparent",
                                        "border": f"1px solid {COLORS['accent1']}",
                                        "color": COLORS["accent1"],
                                        "padding": "8px 16px",
                                        "borderRadius": "6px",
                                        "cursor": "pointer",
                                        "fontSize": "14px",
                                        "fontFamily": "inherit",
                                        "alignSelf": "flex-end",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),

                html.Div(id="kpi-cards", style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

                html.Div(
                    style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
                    children=[
                        html.Div(style={"flex": "3", "minWidth": "400px",
                                        "background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                                        "borderRadius": "8px", "padding": "20px"},
                                 children=[
                                     section_title("Launches per Year"),
                                     html.P("Drag to zoom · Double-click to reset", style={
                                         "fontSize": "11px", "color": COLORS["muted"],
                                         "marginTop": "-10px", "marginBottom": "8px",
                                     }),
                                     dcc.Graph(id="launches-per-year", config={"displayModeBar": False}),
                                 ]),

                        html.Div(style={"flex": "1", "minWidth": "280px",
                                        "background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                                        "borderRadius": "8px", "padding": "20px"},
                                 children=[section_title("Mission Status Distribution"), dcc.Graph(id="status-donut", config={"displayModeBar": False})]),
                    ],
                ),

                html.Div(
                    style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"},
                    children=[
                        html.Div(style={"flex": "1", "minWidth": "340px",
                                        "background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                                        "borderRadius": "8px", "padding": "20px"},
                                 children=[
                                     section_title("Top 15 Companies by Mission Count"),
                                     color_legend([
                                         (COLORS["accent2"], "Fewer missions"),
                                         (COLORS["accent1"], "More missions"),
                                     ]),
                                     dcc.Graph(id="top-companies-bar", config={"displayModeBar": False}),
                                 ]),

                        html.Div(style={"flex": "1", "minWidth": "340px",
                                        "background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                                        "borderRadius": "8px", "padding": "20px"},
                                 children=[
                                     section_title("Success Rate by Top 15 Companies"),
                                     color_legend([
                                         (COLORS["success"], "90 – 100%"),
                                         (COLORS["partial"], "70 – 89%"),
                                         (COLORS["failure"], "< 70%"),
                                     ]),
                                     dcc.Graph(id="success-rate-bar", config={"displayModeBar": False}),
                                 ]),
                    ],
                ),

                html.Div(
                    style={"background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                           "borderRadius": "8px", "padding": "20px", "marginBottom": "20px"},
                    children=[section_title("Launch Activity Heatmap (Year × Decade)"),
                               dcc.Graph(id="heatmap", config={"displayModeBar": False})],
                ),

                html.Div(
                    style={"background": COLORS["panel"], "border": f"1px solid {COLORS['border']}",
                           "borderRadius": "8px", "padding": "20px"},
                    children=[
                        html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "8px"},
                                 children=[
                                     section_title("Mission Data Table"),
                                     html.Span(id="table-row-count", style={"fontSize": "12px", "color": COLORS["muted"]}),
                                 ]),
                        html.P([
                            "Use the filter row below each column header to search. Click the Aa button to toggle case-sensitive matching.",
                            html.Br(),
                            "Click the arrows next to a column header to sort.",
                        ], style={"fontSize": "13px", "color": COLORS["muted"], "marginTop": "0", "marginBottom": "14px", "lineHeight": "1.7"}),
                        dash_table.DataTable(
                            id="data-table",
                            columns=[
                                {"name": "Company",       "id": "Company",       "type": "text"},
                                {"name": "Mission",       "id": "Mission",       "type": "text"},
                                {"name": "Date",          "id": "Date",          "type": "datetime"},
                                {"name": "Rocket",        "id": "Rocket",        "type": "text"},
                                {"name": "Location",      "id": "Location",      "type": "text"},
                                {"name": "Rocket Status", "id": "RocketStatus",  "type": "text"},
                                {"name": "Price (M$)",    "id": "Price",         "type": "numeric"},
                                {"name": "Status",        "id": "MissionStatus", "type": "text"},
                            ],
                            data=[],
                            page_size=15,
                            sort_action="native",
                            sort_mode="multi",
                            filter_action="native",
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": COLORS["bg"],
                                "color": COLORS["accent1"],
                                "fontWeight": "600",
                                "fontSize": "12px",
                                "border": f"1px solid {COLORS['border']}",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px",
                            },
                            style_cell={
                                "backgroundColor": COLORS["panel"],
                                "color": COLORS["text"],
                                "fontSize": "13px",
                                "border": f"1px solid {COLORS['border']}",
                                "padding": "10px 14px",
                                "fontFamily": "Inter, Arial, sans-serif",
                                "maxWidth": "200px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                            },
                            style_filter={
                                "backgroundColor": COLORS["bg"],
                                "color": COLORS["text"],
                                "border": f"1px solid {COLORS['border']}",
                            },
                            style_data_conditional=[
                                {"if": {"filter_query": '{MissionStatus} = "Success"',    "column_id": "MissionStatus"},
                                 "color": COLORS["success"], "fontWeight": "600"},
                                {"if": {"filter_query": '{MissionStatus} = "Failure"',    "column_id": "MissionStatus"},
                                 "color": COLORS["failure"], "fontWeight": "600"},
                                {"if": {"filter_query": '{MissionStatus} = "Partial Failure"', "column_id": "MissionStatus"},
                                 "color": COLORS["partial"], "fontWeight": "600"},
                                {"if": {"filter_query": '{MissionStatus} = "Prelaunch Failure"', "column_id": "MissionStatus"},
                                 "color": COLORS["prelaunch"], "fontWeight": "600"},
                                {"if": {"row_index": "odd"}, "backgroundColor": "#0d1117"},
                            ],
                        ),
                    ],
                ),

            ],
        ),

        html.Div(
            style={"borderTop": f"1px solid {COLORS['border']}", "padding": "16px 40px",
                   "textAlign": "center", "fontSize": "12px", "color": COLORS["muted"]},
            children=["Space Missions Dashboard · Rely Health Case Study"],
        ),
    ],
)


def apply_filters(year_range, companies, statuses, rocket_statuses):
    fdf = df.copy()
    if (year_range and len(year_range) == 2
            and year_range[0] is not None and year_range[1] is not None):
        fdf = fdf[(fdf["Year"] >= year_range[0]) & (fdf["Year"] <= year_range[1])]
    if companies:
        fdf = fdf[fdf["Company"].isin(companies)]
    if statuses:
        fdf = fdf[fdf["MissionStatus"].isin(statuses)]
    if rocket_statuses:
        fdf = fdf[fdf["RocketStatus"].isin(rocket_statuses)]
    return fdf


def empty_fig(msg="No data for selection"):
    fig = go.Figure()
    fig.update_layout(**base_layout(
        annotations=[dict(text=msg, x=0.5, y=0.5, xref="paper", yref="paper",
                          showarrow=False, font=dict(color=COLORS["muted"], size=14))],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=300,
    ))
    return fig


@app.callback(
    Output("year-slider",           "value"),
    Output("company-filter",        "value"),
    Output("status-filter",         "value"),
    Output("rocket-status-filter",  "value"),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return [min_year, max_year], [], [], []


@app.callback(
    Output("kpi-cards",           "children"),
    Output("launches-per-year",   "figure"),
    Output("status-donut",        "figure"),
    Output("top-companies-bar",   "figure"),
    Output("success-rate-bar",    "figure"),
    Output("heatmap",             "figure"),
    Output("data-table",          "data"),
    Output("table-row-count",     "children"),
    Input("year-slider",          "value"),
    Input("company-filter",       "value"),
    Input("status-filter",        "value"),
    Input("rocket-status-filter", "value"),
)
def update_all(year_range, companies, statuses, rocket_statuses):
    fdf = apply_filters(year_range, companies, statuses, rocket_statuses)
    total = len(fdf)

    if total == 0:
        cards = [kpi_card("Total Missions", "0"), kpi_card("Success Rate", "—"),
                 kpi_card("Companies", "0"), kpi_card("Year Range", "—")]
    else:
        n_success   = len(fdf[fdf["MissionStatus"] == "Success"])
        s_rate      = round(n_success / total * 100, 2)
        n_companies = fdf["Company"].nunique()
        _yrs        = fdf["Year"].dropna()
        yr_min      = int(_yrs.min()) if not _yrs.empty else min_year
        yr_max      = int(_yrs.max()) if not _yrs.empty else max_year
        cards = [
            kpi_card("Total Missions",   f"{total:,}",           "filtered launches",       COLORS["accent1"]),
            kpi_card("Success Rate",     f"{s_rate}%",           f"{n_success:,} successes", COLORS["success"]),
            kpi_card("Companies",        f"{n_companies:,}",     "unique organisations",    COLORS["accent2"]),
            kpi_card("Year Span",        f"{yr_min}–{yr_max}",   f"{yr_max - yr_min + 1} years", COLORS["accent3"]),
        ]

    if total == 0:
        empty = empty_fig()
        return cards, empty, empty, empty, empty, empty, [], "0 rows"

    by_year = fdf.groupby("Year").size().reset_index(name="Launches")
    fig_year = go.Figure()
    fig_year.add_trace(go.Scatter(
        x=by_year["Year"], y=by_year["Launches"],
        mode="lines+markers",
        line=dict(color=COLORS["accent1"], width=2),
        marker=dict(size=4, color=COLORS["accent1"]),
        fill="tozeroy",
        fillcolor="rgba(88, 166, 255, 0.10)",
        name="Launches",
        hovertemplate="<b>%{x}</b><br>Launches: %{y}<extra></extra>",
    ))
    fig_year.update_layout(**base_layout(
        height=280, xaxis_title=None, yaxis_title="Missions", showlegend=False,
    ))

    status_counts = fdf["MissionStatus"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    colors_list = [STATUS_COLORS.get(s, COLORS["muted"]) for s in status_counts["Status"]]
    fig_donut = go.Figure(go.Pie(
        labels=status_counts["Status"],
        values=status_counts["Count"],
        hole=0.55,
        marker=dict(colors=colors_list, line=dict(color=COLORS["bg"], width=2)),
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))
    fig_donut.update_layout(**base_layout(
        height=280,
        showlegend=True,
        legend=dict(orientation="v", x=1, y=0.5, font=dict(size=11)),
        annotations=[dict(text=f"<b>{total:,}</b><br>total", x=0.5, y=0.5,
                          font=dict(color=COLORS["text"], size=13), showarrow=False)],
    ))

    top15 = (fdf.groupby("Company").size()
               .reset_index(name="Count")
               .sort_values("Count", ascending=True)
               .tail(15))
    fig_bar = go.Figure(go.Bar(
        x=top15["Count"], y=top15["Company"],
        orientation="h",
        marker=dict(
            color=top15["Count"],
            colorscale=[[0, COLORS["accent2"]], [1, COLORS["accent1"]]],
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Missions: %{x}<extra></extra>",
    ))
    fig_bar.update_layout(**base_layout(
        height=380, xaxis_title="Missions", yaxis_title=None, showlegend=False,
    ))

    company_stats = (fdf.groupby("Company")
                       .agg(Total=("MissionStatus", "count"),
                            Successes=("MissionStatus", lambda x: (x == "Success").sum()))
                       .reset_index())
    company_stats["SuccessRate"] = (company_stats["Successes"] / company_stats["Total"] * 100).round(2)
    top15_companies = fdf.groupby("Company").size().nlargest(15).index.tolist()
    sr_df = (company_stats[company_stats["Company"].isin(top15_companies)]
                .sort_values("SuccessRate", ascending=True))
    fig_sr = go.Figure(go.Bar(
        x=sr_df["SuccessRate"], y=sr_df["Company"],
        orientation="h",
        marker=dict(
            color=sr_df["SuccessRate"],
            colorscale=[[0, COLORS["failure"]], [0.7, COLORS["partial"]], [1, COLORS["success"]]],
            cmin=0, cmax=100,
            line=dict(width=0),
        ),
        hovertemplate="<b>%{y}</b><br>Success Rate: %{x:.2f}%<extra></extra>",
    ))
    fig_sr.update_layout(**base_layout(
        height=380,
        xaxis_title="Success Rate (%)",
        xaxis=dict(range=[0, 100]),
        yaxis_title=None,
        showlegend=False,
    ))

    heatmap_df = fdf[fdf["Year"].notna()].copy()
    heatmap_df["Year"] = heatmap_df["Year"].astype(int)
    heatmap_df["Decade"] = (heatmap_df["Year"] // 10 * 10).astype(str) + "s"
    heatmap_df["YearInDecade"] = heatmap_df["Year"] % 10
    heat_pivot = (heatmap_df.groupby(["Decade", "YearInDecade"]).size()
                             .reset_index(name="Count")
                             .pivot(index="Decade", columns="YearInDecade", values="Count")
                             .fillna(0))
    heat_pivot.columns = [f"+{c}" for c in heat_pivot.columns]
    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0.0, "#1c2d3f"], [1.0, COLORS["accent1"]]],
        hovertemplate="<b>%{y} +%{x}</b><br>Launches: %{z}<extra></extra>",
        showscale=True,
        colorbar=dict(
            tickcolor=COLORS["muted"],
            tickfont=dict(color=COLORS["muted"], size=11),
            title=dict(text="Launches", font=dict(color=COLORS["muted"], size=12)),
            thickness=14,
        ),
    ))
    fig_heat.update_layout(**base_layout(
        height=300,
        xaxis_title="Year within decade",
        yaxis_title=None,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    ))

    desired_cols = ["Company", "Mission", "Date", "Rocket", "Location",
                    "RocketStatus", "Price", "MissionStatus"]
    table_df = fdf[[c for c in desired_cols if c in fdf.columns]].copy()
    if "Date" in table_df.columns:
        table_df["Date"] = table_df["Date"].astype(str).str[:10]
    if "Price" in table_df.columns:
        table_df["Price"] = table_df["Price"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

    return cards, fig_year, fig_donut, fig_bar, fig_sr, fig_heat, table_df.to_dict("records"), f"{total:,} rows"


if __name__ == "__main__":
    print("\n Space Missions Dashboard starting...")
    print("   Open http://127.0.0.1:8050 in your browser\n")
    app.run(debug=True, port=8050)
