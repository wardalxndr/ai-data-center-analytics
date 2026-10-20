"""AI Data Center one-pager dashboard (Streamlit) - white/blue clean edition.

Run: streamlit run dashboard/app.py
Data: pipeline/make_dashboard_data.py -> data/dashboard_data.json
Source: Epoch AI dataset (CC-BY), live snapshot with drift note vs the
pinned snapshot in ADR 0006 (94 sites / 560 rows).
"""
from contextlib import contextmanager
import base64
import json
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dashboard_data.json"

BLUE = "#2F6BF0"
RAMP = ["#2F6BF0", "#5B8DEF", "#8AB1F5", "#AFC9FA", "#C7DAFB"]
INK = "#17233D"
GREY = "#667085"
BORDER = "#E7ECF4"

C_NA = "#2F6BF0"
C_APAC = "#5B8DEF"
C_EMEA = "#8AB1F5"
C_OTHER = "#C7DAFB"

st.set_page_config(layout="wide", page_title="AI Data Center Analytics",
                   page_icon=":factory:", initial_sidebar_state="expanded")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: INK; }
.stApp { background: #FFFFFF; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1620px; padding-top: .8rem; padding-bottom: 1.4rem; }
[data-testid="stSidebar"] { background: #F7F9FC; border-right: 1px solid BORDER; }
[data-testid="stSidebar"] .block-container { padding-top: 1.4rem; }

.app-name { font-size: 15px; font-weight: 700; color: INK; }
.avatar { display: inline-flex; width: 32px; height: 32px; border-radius: 50%;
  background: BLUE; color: #fff; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px; }

.headline { font-size: 27px; font-weight: 700; color: INK; letter-spacing: -.2px; }
.subline { color: GREY; font-size: 13px; margin-bottom: 4px; }

.card, [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF;
  border: 1px solid BORDER !important; border-radius: 16px !important;
  box-shadow: 0 1px 3px rgba(23,35,61,.04); }
[data-testid="stVerticalBlockBorderWrapper"] { padding: 18px 22px 12px; }

.kpi { padding: 18px 20px; border: 1px solid BORDER; border-radius: 16px;
  background: #fff; box-shadow: 0 1px 3px rgba(23,35,61,.04); height: 100%; }
.kpi-label { font-size: 11px; font-weight: 700; letter-spacing: 1px;
  text-transform: uppercase; color: GREY; }
.kpi-value { font-size: 33px; font-weight: 700; color: INK; line-height: 1.2; }
.kpi-note { font-size: 12px; color: GREY; margin-top: 1px; }

.callout { background: #EAF1FE; border: 1px solid #C7DAFB; border-radius: 12px;
  padding: 14px 20px; }
.callout-title { font-size: 13.5px; font-weight: 700; color: #1B44B8;
  letter-spacing: .2px; }
.callout-sub { font-size: 13px; color: #3D4A63; margin-top: 2px; }

.tile-title { font-size: 15px; font-weight: 700; color: INK; }
.tile-note { font-size: 12px; color: GREY; }

.pill { background: #F5F8FF; border: 1px solid #E3EAFB; border-radius: 10px;
  padding: 8px 12px; font-size: 12.5px; color: #44515F; }
.mrow { display: flex; align-items: center; justify-content: space-between;
  padding: 4px 0; font-size: 12.5px; color: INK; }
.mrow .n { color: GREY; }
.dot { display: inline-block; width: 11px; height: 11px; border-radius: 3px;
  margin-right: 8px; }

.orow { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.oic { flex: 0 0 34px; height: 30px; display: inline-flex; align-items: center;
  justify-content: center; }
.oic img { width: 24px; height: 24px; object-fit: contain; }
.olbl { flex: 0 0 88px; font-size: 12.5px; color: GREY; }
.obar { height: 26px; border-radius: 8px; }
.opct { margin-left: auto; font-size: 12.5px; font-weight: 600; color: INK;
  width: 58px; text-align: right; }

.worklist { max-height: 288px; overflow: auto; }
.worklist table { width: 100%; border-collapse: collapse; font-size: 13px; }
.worklist th { text-align: left; font-size: 10.5px; font-weight: 700;
  letter-spacing: .8px; text-transform: uppercase; color: GREY;
  border-bottom: 1px solid BORDER; padding: 7px 10px; position: sticky;
  top: 0; background: #fff; }
.worklist td { padding: 7px 10px; border-bottom: 1px solid #F1F4F9; color: INK; }
.worklist td.flag { font-size: 15px; }

.footer { color: GREY; font-size: 12px; }
div[data-baseweb="select"] > div { border-radius: 10px; }
button[kind="secondary"] { border-radius: 999px !important; }
</style>
""".replace("INK", INK).replace("GREY", GREY).replace(
    "BORDER", BORDER).replace("BLUE", BLUE)


def fmt_int(n):
    return f"{n:,}"


def fmt_pct(p, dec=1):
    return f"{p * 100:.{dec}f}%"


@st.cache_data
def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


d = load(DATA)
k = d["kpis"]
regions = [[n, float(v)] for n, v in d["regions"]]
total_power = sum(v for _, v in regions)
countries = d["countries"]
owners = d["owners"]
velocity = d["velocity"]
region_adds = d["region_additions"]

ISO3 = {"United States": "USA", "Malaysia": "MYS", "China": "CHN",
        "United Kingdom": "GBR", "Finland": "FIN", "Indonesia": "IDN",
        "Norway": "NOR", "Australia": "AUS", "Portugal": "PRT",
        "Iceland": "ISL"}
FLAGS = {"United States": "US", "Malaysia": "MY", "China": "CN",
         "United Kingdom": "GB", "Finland": "FI", "Indonesia": "ID",
         "Norway": "NO", "Australia": "AU", "Portugal": "PT",
         "Iceland": "IS", "Sweden": "SE", "United Arab Emirates": "AE",
         "Canada": "CA", "Mexico": "MX", "Brazil": "BR", "Chile": "CL",
         "Argentina": "AR", "Japan": "JP", "India": "IN",
         "South Korea": "KR", "Singapore": "SG", "Taiwan": "TW",
         "Hong Kong": "HK", "New Zealand": "NZ", "Vietnam": "VN",
         "Thailand": "TH", "Philippines": "PH", "Germany": "DE",
         "France": "FR", "Ireland": "IE", "Netherlands": "NL",
         "Spain": "ES", "Qatar": "QA"}


def flag(name):
    code = FLAGS.get(name)
    if not code:
        return "🌐"
    return (f'<img src="https://flagcdn.com/w20/{code.lower()}.png" '
            f'width="18" height="12" style="border-radius:2px;'
            f'margin-right:6px">')


# ---------- charts ----------
def area_chart():
    years = [str(y) for y, _, _ in region_adds]
    series = [("North America", C_NA), ("APAC", C_APAC), ("EMEA", C_EMEA)]
    fig = go.Figure()
    for name, color in series:
        vals = [blk.get(name, 0) for _, blk, _ in region_adds]
        fig.add_trace(go.Scatter(
            x=years, y=vals, name=name, mode="lines", line=dict(width=0),
            stackgroup="one", fillcolor=color, hovertemplate=name +
            ": %{y:,.0f} MW<extra></extra>"))
    last_y, last_blk, last_n = region_adds[-1]
    last_mw = sum(last_blk.values())
    fig.add_annotation(
        x=years[-1], y=last_mw, text=f"{fmt_int(last_mw)} MW in {last_y}",
        showarrow=True, arrowhead=0, ax=-30, ay=-34,
        font=dict(size=12, color=INK, family="Inter, sans-serif"),
        bgcolor="#EAF1FE", bordercolor="#C7DAFB", borderpad=4)
    fig.update_layout(
        height=296, margin=dict(l=6, r=6, t=8, b=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=GREY, size=12),
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right",
                    font=dict(size=12)), dragmode=False)
    fig.update_xaxes(showline=True, linecolor=BORDER, tickfont=dict(
        size=11, color=GREY))
    fig.update_yaxes(gridcolor="#F1F4F9", tickfont=dict(size=11, color=GREY),
                     tickvals=[0, 2500, 5000, 7500],
                     ticktext=["0", "2,500", "5,000", "7,500"])
    return fig


def donut_chart():
    labels = [n for n, _ in regions]
    vals = [v for _, v in regions]
    total = sum(vals)
    fig = go.Figure(go.Pie(
        labels=labels, values=vals, hole=.66, sort=False,
        direction="clockwise",
        marker=dict(colors=[C_NA, C_APAC, C_EMEA]),
        text=[fmt_pct(v / total, 0) if v / total >= .05 else ""
              for v in vals],
        textinfo="text", textposition="inside",
        insidetextorientation="horizontal", showlegend=False,
        hovertemplate="%{label}: %{value:,.0f} MW (%{percent})<extra></extra>"))
    fig.update_traces(textfont=dict(
        color=["#FFFFFF", INK, INK], size=13, family="Inter, sans-serif"))
    fig.add_annotation(
        text=f"<b style='font-size:20px;color:{INK}'>{k['total_gw']} GW</b>"
             f"<br><span style='font-size:12px;color:{GREY}'>"
             f"total power</span>",
        showarrow=False, font=dict(family="Inter, sans-serif"))
    fig.update_layout(height=296, margin=dict(l=4, r=4, t=4, b=4),
                      paper_bgcolor="rgba(0,0,0,0)")
    return fig


def map_chart(height=330):
    bins = [(10000, "#1E4FD8"), (1000, "#2F6BF0"), (100, "#7D9EF6"),
            (10, "#B7CCFB"), (0, "#DCE8FE")]

    def rank(mw):
        for i, (lo, _) in enumerate(bins):
            if mw >= lo:
                return len(bins) - 1 - i
        return 0
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=[ISO3.get(c, "") for c, mw, _ in countries],
        z=[rank(mw) for _, mw, _ in countries],
        customdata=[(c, mw, n) for c, mw, n in countries],
        zmin=0, zmax=4, showscale=False,
        colorscale=[[0.0, "#DCE8FE"], [0.125, "#DCE8FE"],
                    [0.125, "#B7CCFB"], [0.375, "#B7CCFB"],
                    [0.375, "#7D9EF6"], [0.625, "#7D9EF6"],
                    [0.625, "#2F6BF0"], [0.875, "#2F6BF0"],
                    [0.875, "#1E4FD8"], [1.0, "#1E4FD8"]],
        marker=dict(line=dict(color="#FFFFFF", width=1)),
        hovertemplate="%{customdata[0]}: %{customdata[1]:,.0f} MW · "
                      "%{customdata[2]} sites<extra></extra>"))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
        geo=dict(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#EEF2F8",
                 showcountries=True, countrycolor="#FFFFFF",
                 showcoastlines=False, showframe=False, resolution=50,
                 projection=dict(type="natural earth", scale=1.18),
                 center=dict(lat=12, lon=-20)))
    return fig


def data_uri(filename):
    path = Path(ROOT) / "dashboard" / "assets" / filename
    mime = "image/jpeg" if path.suffix == ".jpg" else "image/png"
    return ("data:%s;base64,%s" % (mime, base64.b64encode(
        path.read_bytes()).decode()))


def owners_html(mode="top3"):
    if mode == "all":    # drill-down page: every tracked owner
        rows = [(n, float(v)) for n, v in owners]
        others_mw = total_power - sum(v for _, v in rows)
        rows.append(("Others", others_mw))
    else:                # overview: top 3 + aggregated rest
        rows = [(n, float(v)) for n, v in owners[:3]]
        rows.append(("Others", total_power - sum(v for _, v in rows)))
    max_v = max(v for _, v in rows)
    icons = {"Google": "https://www.google.com/favicon.ico",
             "Meta": "https://cdn.simpleicons.org/meta/0668E2",
             "Amazon": "https://www.amazon.com/favicon.ico",
             "Microsoft": "https://www.microsoft.com/favicon.ico",
             "Oracle": "https://www.oracle.com/favicon.ico",
             "Huawei": "https://www.huawei.com/favicon.ico",
             "SpaceXAI": data_uri("spacex.jpg"),
             "CoreWeave": data_uri("coreweave.jpg")}
    initials = {}
    bar_colors = [C_NA, C_APAC, C_EMEA, "#B7CCFB", "#8AB1F5", "#AFC9FA",
                  "#C7DAFB", "#B7CCFB"]
    html = ""
    for i, (name, v) in enumerate(rows):
        if name in icons:
            ic = (f'<img src="{icons[name]}" width="20" height="20"'
                  f' onerror="this.style.display=\'none\'">')
        elif name in initials:
            ic = (f'<span style="font-size:10px;font-weight:700;color:{INK};'
                  f'background:#EDF2FE;border-radius:6px;padding:3px 5px">'
                  f'{initials[name]}</span>')
        else:
            ic = ""
        col = "#D3DCE9" if name == "Others" else bar_colors[i % 8]
        html += (f'<div class="orow"><span class="oic">{ic}</span>'
                 f'<span class="olbl">{name}</span>'
                 f'<div class="obar" style="width:{v / max_v * 100:.1f}%;'
                 f'background:{col}"></div>'
                 f'<span class="opct">{fmt_pct(v / total_power)}</span>'
                 f'</div>')
    return html


def build_days_chart():
    xs = [y for y, _ in velocity]
    ys = [v for _, v in velocity]
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="lines+markers",
        line=dict(color=C_NA, width=2), marker=dict(size=8, color=C_NA),
        hovertemplate="%{x}: %{y:,.0f} days<extra></extra>"))
    fig.add_annotation(
        x=xs[0], y=ys[0], text=f"{fmt_int(ys[0])} days",
        showarrow=True, arrowhead=0, ax=26, ay=-24,
        font=dict(size=12, color=INK, family="Inter, sans-serif"))
    fig.add_annotation(
        x=xs[-1], y=ys[-1], text=f"{fmt_int(ys[-1])} days",
        showarrow=True, arrowhead=0, ax=-8, ay=-24,
        font=dict(size=12, color=INK, family="Inter, sans-serif"))
    fig.update_layout(
        height=286, margin=dict(l=6, r=6, t=10, b=6),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=GREY, size=12),
        dragmode=False)
    fig.update_xaxes(showline=True, linecolor=BORDER, tickfont=dict(
        size=11, color=GREY))
    fig.update_yaxes(gridcolor="#F1F4F9", tickfont=dict(size=11, color=GREY),
                     tickvals=[0, 500, 1000, 1500, 2000],
                     ticktext=["0", "500", "1,000", "1,500", "2,000"])
    return fig


@contextmanager
def tile_open(title, note=None):
    with st.container(border=True):
        if note:
            h1, h2 = st.columns([.6, .4])
            h1.markdown(f'<div class="tile-title">{title}</div>',
                        unsafe_allow_html=True)
            h2.markdown(f'<div class="tile-note" style="text-align:right;'
                        f'margin-top:3px">{note}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="tile-title">{title}</div>',
                        unsafe_allow_html=True)
        yield


# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div class="app-name">AI Data Center Analytics</div>',
                unsafe_allow_html=True)
    st.write("")
    nav = st.radio("Navigation",
                   ["Overview", "Sites", "Map", "Owners", "Countries",
                    "Trends"], label_visibility="collapsed")
    st.write("")
    st.caption("live Epoch pull (CC-BY) · snapshot " + d["snapshot"])

st.markdown(CSS, unsafe_allow_html=True)

if nav != "Overview":
    st.markdown(f'<div class="headline">{nav}</div>', unsafe_allow_html=True)
    if nav == "Sites":
        st.markdown(f'<div class="subline">{k["sites"]} sites tracked · '
                    'sort by current MW · owner merged from raw CSV</div>',
                    unsafe_allow_html=True)
        st.write("")
        with tile_open("All sites", fmt_int(k["sites"]) + " rows"):
            body = ""
            for s in d["sites_all"]:
                body += (f"<tr><td>{s['name']}</td><td>{s['owner']}</td>"
                         f"<td>{flag(s['country'])}{s['country']}</td>"
                         f"<td>{fmt_int(round(s['mw']))}</td></tr>")
            st.markdown(
                '<div class="worklist" style="max-height:560px"><table>'
                '<thead><tr><th>Name</th><th>Owner</th><th>Country</th>'
                '<th>Current MW</th></tr></thead>'
                f'<tbody>{body}</tbody></table></div>',
                unsafe_allow_html=True)
    elif nav == "Map":
        st.markdown('<div class="subline">current MW by country, color = '
                    'MW bucket</div>', unsafe_allow_html=True)
        st.write("")
        with tile_open("Current MW by country", "color = MW bucket"):
            c_map, c_leg = st.columns([.78, .22], gap="small")
            c_map.plotly_chart(map_chart(560), width="stretch",
                               config={"displayModeBar": False})
            with c_leg:
                st.markdown('<div class="mrow" style="font-size:11.5px;'
                            'color:' + GREY + '">MW (current)</div>',
                            unsafe_allow_html=True)
                legend_bins = [("10,000+", "#1E4FD8"),
                               ("1,000 - 9,999", "#2F6BF0"),
                               ("100 - 999", "#7D9EF6"),
                               ("10 - 99", "#B7CCFB"), ("< 10", "#DCE8FE")]
                for label, col in legend_bins:
                    st.markdown(f'<div class="mrow"><span><span class="dot" '
                                f'style="background:{col}"></span>{label}'
                                f'</span></div>', unsafe_allow_html=True)
    elif nav == "Owners":
        st.markdown(f'<div class="subline">current MW share by owner · '
                    f'total {k["total_gw"]} GW</div>', unsafe_allow_html=True)
        st.write("")
        with tile_open("All owners by MW", "tracked owners, rest pooled"):
            st.markdown(owners_html("all"), unsafe_allow_html=True)
    elif nav == "Countries":
        st.markdown(f'<div class="subline">{len(d["countries_all"])} '
                    'countries host tracked sites</div>',
                    unsafe_allow_html=True)
        st.write("")
        with tile_open("Countries by MW", "all countries"):
            body = ""
            for c_name, mw, n in d["countries_all"]:
                body += (f"<tr><td>{flag(c_name)}{c_name}</td>"
                         f"<td>{fmt_int(mw)}</td><td>{n}</td></tr>")
            st.markdown(
                '<div class="worklist" style="max-height:560px"><table>'
                '<thead><tr><th>Country</th><th>MW (current)</th>'
                f'<th>Sites</th></tr></thead><tbody>{body}</tbody></table>'
                '</div>', unsafe_allow_html=True)
    elif nav == "Trends":
        st.markdown('<div class="subline">annual additions and build '
                    'velocity, from the timeline table</div>',
                    unsafe_allow_html=True)
        st.write("")
        with tile_open("Annual MW reaching full power", "new site power"):
            st.plotly_chart(area_chart(), width="stretch",
                            config={"displayModeBar": False})
        with tile_open("Avg build days by start year", "start to full power"):
            st.plotly_chart(build_days_chart(), width="stretch",
                            config={"displayModeBar": False})
        with tile_open("Additions per year", "MW added · sites count"):
            body = "".join(
                f"<tr><td>{y}</td><td>{fmt_int(sum(blk.values()))}</td>"
                f"<td>{n}</td></tr>" for y, blk, n in region_adds)
            st.markdown(
                '<div class="worklist" style="max-height:300px"><table>'
                '<thead><tr><th>Year</th><th>MW added</th>'
                f'<th>Sites</th></tr></thead><tbody>{body}</tbody></table>'
                '</div>', unsafe_allow_html=True)
    st.caption("")
    st.markdown('<div class="footer">Source: Epoch AI dataset (CC-BY) · '
                'repo: ai-data-center-analytics</div>',
                unsafe_allow_html=True)
    st.stop()

# ---------- top bar ----------
tb1, tb2, tb3 = st.columns([.6, .2, .2])
tb1.markdown('<div class="app-name" style="font-size:16px">AI Data Center '
             'Analytics</div>', unsafe_allow_html=True)
tb2.selectbox("Region", ["All"], disabled=True, label_visibility="collapsed",
              key="region")
if tb3.button("Share", use_container_width=True, type="secondary"):
    try:
        st.toast("Demo build - repo: ai-data-center-analytics", icon="i")
    except AttributeError:
        pass

st.write("")

# ---------- headline ----------
st.markdown('<div class="headline">AI Data Centers: Where Does the Next '
            'Build Go?</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subline">Epoch AI dataset (CC-BY) · live pull '
            f'{d["snapshot"]} ({d["drift"]["dc"]} sites, '
            f'{d["drift"]["tl"]} timeline rows) · pinned ADR 0006: '
            f'{d["pinned"]["dc"]} / {d["pinned"]["tl"]}</div>',
            unsafe_allow_html=True)
st.write("")

# ---------- KPI row ----------
k1, k2, k3, k4 = st.columns(4, gap="small")


def kpi_col(container, label, value, note=""):
    with container:
        note_html = (f'<div class="kpi-note">{note}</div>' if note else "")
        st.markdown(
            f'<div class="kpi">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>{note_html}'
            f'</div>', unsafe_allow_html=True)


kpi_col(k1, "Sites tracked", fmt_int(k["sites"]))
kpi_col(k2, "Global power", f"{k['total_gw']} GW")
kpi_col(k3, "APAC power", f"{fmt_int(k['apac_mw'])} MW",
        f"{k['apac_sites']} sites, " + fmt_pct(d["apac_share"], 1) +
        " of tracked")
kpi_col(k4, "Avg build days", f"~{fmt_int(k['avg_build_days'])}",
        "start to full power, all sites")
st.write("")

# ---------- callout ----------
drift_txt = ""
if (d["drift"]["dc"], d["drift"]["tl"]) != (d["pinned"]["dc"],
                                            d["pinned"]["tl"]):
    drift_txt = (f" Source is drifting: live {d['drift']['dc']} sites vs "
                 f"pinned {d['pinned']['dc']} (ADR 0006).")
st.markdown(
    f'<div class="callout"><div class="callout-title">EXPAND JOHOR FIRST, '
    f'BATAM NEXT.</div><div class="callout-sub">Malaysia: '
    f'{fmt_int(d["malaysia"]["mw"])} MW ({d["malaysia"]["sites"]} sites) '
    f'vs Indonesia: {fmt_int(d["indonesia"]["mw"])} MW '
    f'({d["indonesia"]["sites"]} site). US holds '
    f'{fmt_pct(d["us_share"], 0)} of tracked MW '
    f'({fmt_int(d["us_mw"])} MW).{drift_txt}</div></div>',
    unsafe_allow_html=True)
st.write("")

# ---------- row: area + donut ----------
a1, a2 = st.columns([.58, .42], gap="small")
with a1:
    with tile_open("Annual MW reaching full power", "new site power, per year"):
        st.plotly_chart(area_chart(), width="stretch",
                        config={"displayModeBar": False})
with a2:
    with tile_open("Power share by region"):
        d1, d2 = st.columns([.5, .5], gap="small")
        d1.plotly_chart(donut_chart(), width="stretch",
                        config={"displayModeBar": False})
        with d2:
            for (n, v), col in zip(regions, [C_NA, C_APAC, C_EMEA]):
                st.markdown(f'<div class="mrow"><span><span class="dot" '
                            f'style="background:{col}"></span>{n}</span>'
                            f'<span class="n">{fmt_int(v)} MW '
                            f'({fmt_pct(v / total_power, 0)})</span></div>',
                            unsafe_allow_html=True)
            st.write("")
            st.markdown('<div class="pill">One country (US) holds 84% of '
                        'tracked power.</div>', unsafe_allow_html=True)
st.write("")

# ---------- row: map + owners ----------
m1, m2 = st.columns([.58, .42], gap="small")
with m1:
    with tile_open("Current MW by country", "color = MW bucket"):
        c_map, c_leg = st.columns([.68, .32], gap="small")
        c_map.plotly_chart(map_chart(), width="stretch",
                           config={"displayModeBar": False})
        with c_leg:
            st.markdown('<div class="mrow" style="font-size:11.5px;color:' +
                        GREY + '">MW (current)</div>',
                        unsafe_allow_html=True)
            legend_bins = [("10,000+", "#1E4FD8"),
                           ("1,000 - 9,999", "#2F6BF0"),
                           ("100 - 999", "#7D9EF6"), ("10 - 99", "#B7CCFB"),
                           ("< 10", "#DCE8FE")]
            for label, col in legend_bins:
                st.markdown(f'<div class="mrow"><span><span class="dot" '
                            f'style="background:{col}"></span>{label}'
                            f'</span></div>', unsafe_allow_html=True)
with m2:
    others_share = 1 - sum(v for _, v in owners) / total_power
    with tile_open("Top owners by MW",
                   fmt_pct(others_share, 0) + " held by others"):
        st.markdown(owners_html("all"), unsafe_allow_html=True)
st.write("")

# ---------- row: countries table + build days ----------
c1, c2 = st.columns([.55, .45], gap="small")
with c1:
    with tile_open("Countries by MW with sites count",
                   "top 10 of " + str(k["sites"]) + " sites"):
        body = ""
        for c_name, mw, n in countries:
            body += (f"<tr><td>{flag(c_name)}{c_name}</td>"
                     f"<td>{fmt_int(mw)}</td><td>{n}</td></tr>")
        st.markdown(
            f'<div class="worklist"><table><thead><tr><th>Country</th>'
            f'<th>MW (current)</th><th>Sites</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>', unsafe_allow_html=True)
with c2:
    with tile_open("Avg build days by start year", "newer starts build faster"):
        st.plotly_chart(build_days_chart(), width="stretch",
                        config={"displayModeBar": False})
    st.caption("")

st.write("")
st.markdown('<div class="footer">Source: Epoch AI dataset (CC-BY) · live '
            'pull ' + d["snapshot"] + ' · pinned snapshot (ADR 0006): 94 '
            'sites / 560 rows · pipeline: Kestra + BigQuery + dbt · '
            'repo: ai-data-center-analytics</div>', unsafe_allow_html=True)
