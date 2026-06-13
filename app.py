import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Zemědělství východní Evropy – FAOSTAT",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS: pěkný design, tmavé kartičky, font ──────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* stránka */
.block-container { padding: 1.2rem 1.5rem 2rem; max-width: 1500px; }
section[data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2130; }
section[data-testid="stSidebar"] * { color: #d0d4e0 !important; }
section[data-testid="stSidebar"] .stRadio label, 
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label { color: #8892a4 !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: .05em; }
section[data-testid="stSidebar"] hr { border-color: #1e2130 !important; }

/* nadpis */
h1 { font-size: 1.35rem !important; font-weight: 600 !important; color: #e8ecf4 !important; letter-spacing: -0.02em; margin-bottom: .1rem !important; }
.subtitle { font-size: 0.78rem; color: #5c6680; margin-bottom: 1rem; }

/* kartičky */
.card {
    background: #141720;
    border: 1px solid #1e2435;
    border-radius: 10px;
    padding: 12px 14px 8px;
    margin-bottom: 0;
    transition: border-color .15s;
}
.card:hover { border-color: #2e3a55; }
.card-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px; }
.card-title { font-size: 13px; font-weight: 500; color: #c8cfe0; }
.card-stat { font-size: 11px; color: #5c6680; text-align: right; max-width: 180px; line-height: 1.3; }

/* legenda nahoře */
.legend-bar { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
.leg { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #8892a4; }
.leg-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }

/* metric čísla */
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 600 !important; color: #e8ecf4 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #5c6680 !important; text-transform: uppercase; letter-spacing: .06em; }
[data-testid="metric-container"] { background: #141720; border: 1px solid #1e2435; border-radius: 10px; padding: 14px 18px !important; }

/* sidebar nadpis sekce */
.sidebar-section { font-size: 0.65rem; text-transform: uppercase; letter-spacing: .1em; color: #3a4258 !important; margin: .8rem 0 .3rem; }
</style>
""", unsafe_allow_html=True)

# ── DATA ──────────────────────────────────────────────────────────────────────
from data import YEARS, COUNTRIES, POP, D, CATEGORIES

# ── HELPERS ──────────────────────────────────────────────────────────────────
def hex_rgba(hex_color: str, alpha: float = 0.35) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def get_vals(key, cid):
    return (D.get(key) or {}).get(cid, [None]*63)

def apply_pc(vals, cid):
    pop = POP.get(cid, [None]*63)
    return [v/p if (v is not None and p) else None for v, p in zip(vals, pop)]

def slice_yrs(vals, yr0, yr1):
    s, e = YEARS.index(yr0), YEARS.index(yr1)+1
    return YEARS[s:e], vals[s:e]

def last_valid(vals):
    for v in reversed(vals):
        if v is not None: return v
    return None

def has_data(keys, cid):
    return any(any(v is not None for v in get_vals(k, cid)) for k in keys)

def fmt(v, unit, pc=False):
    if v is None: return "—"
    suf = "/os." if pc else ""
    if unit in ("tis. ha","tis. ks","tis. t"): return f"{v:,.0f} {unit}{suf}"
    if unit == "mld. USD": return f"{v:.2f} {unit}{suf}"
    return f"{v:.2f} {unit}{suf}"

def trend_pct(vals):
    clean = [v for v in vals if v is not None]
    if len(clean) < 10: return None
    old = np.mean(clean[:5])
    new = np.mean(clean[-5:])
    if old == 0: return None
    return (new - old) / old * 100

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 FAOSTAT")
    st.markdown("**Zemědělství · Východní Evropa**")
    st.markdown("<div style='font-size:.75rem;color:#3a4258'>1961 – 2023</div>", unsafe_allow_html=True)
    st.divider()

    st.markdown("<div class='sidebar-section'>Kategorie</div>", unsafe_allow_html=True)
    category = st.radio(
        "", label_visibility="collapsed",
        options=[c["id"] for c in CATEGORIES],
        format_func=lambda x: next(c["label"] for c in CATEGORIES if c["id"]==x),
    )
    cat_cfg = next(c for c in CATEGORIES if c["id"]==category)

    st.divider()
    st.markdown("<div class='sidebar-section'>Zobrazení</div>", unsafe_allow_html=True)

    if cat_cfg["multi_select"]:
        selected_metrics = st.multiselect(
            "", label_visibility="collapsed",
            options=[m["id"] for m in cat_cfg["metrics"]],
            default=cat_cfg["default_selected"],
            format_func=lambda x: next(m["label"] for m in cat_cfg["metrics"] if m["id"]==x),
        ) or cat_cfg["default_selected"][:1]
    else:
        sel = st.radio(
            "", label_visibility="collapsed",
            options=[m["id"] for m in cat_cfg["metrics"]],
            format_func=lambda x: next(m["label"] for m in cat_cfg["metrics"] if m["id"]==x),
        )
        selected_metrics = [sel]

    st.divider()
    st.markdown("<div class='sidebar-section'>Přepočet</div>", unsafe_allow_html=True)
    per_capita = st.toggle("Na osobu", value=False)

    st.divider()
    st.markdown("<div class='sidebar-section'>Časové období</div>", unsafe_allow_html=True)
    yr0, yr1 = st.slider("", label_visibility="collapsed",
                          min_value=1961, max_value=2023, value=(1961, 2023))

    st.divider()
    st.markdown("<div class='sidebar-section'>Země</div>", unsafe_allow_html=True)
    sel_countries = st.multiselect(
        "", label_visibility="collapsed",
        options=[c["id"] for c in COUNTRIES],
        default=[c["id"] for c in COUNTRIES],
        format_func=lambda x: next(c["name"] for c in COUNTRIES if c["id"]==x),
    ) or [c["id"] for c in COUNTRIES]

    st.divider()
    st.markdown("<div class='sidebar-section'>Mřížka</div>", unsafe_allow_html=True)
    n_cols = st.select_slider("", label_visibility="collapsed",
                               options=[1,2,3,4], value=3)

    st.markdown("""
    <div style='font-size:.68rem;color:#2a3048;margin-top:1.5rem;line-height:1.6'>
    Zdroj: FAOSTAT / FAO<br>
    Populace: OSN WPP<br>
    Vytvořeno s Streamlit + Plotly
    </div>""", unsafe_allow_html=True)

# ── PŘÍPRAVA ─────────────────────────────────────────────────────────────────
active_metrics = [m for m in cat_cfg["metrics"] if m["id"] in selected_metrics]
metric_keys    = [m["key"] for m in active_metrics]
is_stacked     = cat_cfg.get("stacked", False) and len(active_metrics) > 1

visible = [c for c in COUNTRIES if c["id"] in sel_countries and has_data(metric_keys, c["id"])]

# ── HEADER ───────────────────────────────────────────────────────────────────
cat_label = cat_cfg["label"]
pc_label  = " · na osobu" if per_capita else ""
st.markdown(f"<h1>{cat_label}{pc_label}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Časová řada {yr0}–{yr1} &nbsp;·&nbsp; {len(visible)} zemí &nbsp;·&nbsp; Zdroj: FAOSTAT</div>", unsafe_allow_html=True)

# ── LEGENDA ───────────────────────────────────────────────────────────────────
if len(active_metrics) > 1:
    parts = []
    for m in active_metrics:
        label = m['label'].split(' (')[0]
        color = m['color']
        parts.append(f"<span class='leg'><span class='leg-dot' style='background:{color}'></span>{label}</span>")
    leg_html = "<div class='legend-bar'>" + "".join(parts) + "</div>"
    st.markdown(leg_html, unsafe_allow_html=True)

# ── SUMMARY METRIKY ───────────────────────────────────────────────────────────
if visible and active_metrics:
    fm = active_metrics[0]
    vals_dict = {}
    for c in visible:
        v = get_vals(fm["key"], c["id"])
        if per_capita: v = apply_pc(v, c["id"])
        lv = last_valid(v)
        if lv is not None: vals_dict[c["id"]] = lv

    if vals_dict:
        top = sorted(vals_dict.items(), key=lambda x: x[1], reverse=True)[:4]
        mcols = st.columns(len(top))
        for col, (cid, val) in zip(mcols, top):
            cname = next(c["name"] for c in COUNTRIES if c["id"]==cid)
            all_v = get_vals(fm["key"], cid)
            if per_capita: all_v = apply_pc(all_v, cid)
            pct = trend_pct(all_v)
            delta_str = f"{pct:+.0f} % (vs. 60. léta)" if pct is not None else None
            col.metric(cname, fmt(val, fm["unit"], per_capita), delta=delta_str)

    st.markdown("<div style='margin-bottom:.5rem'></div>", unsafe_allow_html=True)

# ── SMALL MULTIPLES GRID ──────────────────────────────────────────────────────
if not visible:
    st.warning("Pro vybranou kombinaci nejsou dostupná data.")
    st.stop()

rows = [visible[i:i+n_cols] for i in range(0, len(visible), n_cols)]

for row in rows:
    cols = st.columns(n_cols, gap="small")
    for col, ctry in zip(cols, row):
        with col:
            stat_parts = []
            fig = go.Figure()
            has_any = False

            for mi, m in enumerate(active_metrics):
                raw = get_vals(m["key"], ctry["id"])
                if per_capita:
                    raw = apply_pc(raw, ctry["id"])
                yrs, vals = slice_yrs(raw, yr0, yr1)
                y = [v if v is not None else float("nan") for v in vals]
                if not any(not np.isnan(v) for v in y): continue
                has_any = True

                lv = last_valid(vals)
                if lv is not None:
                    stat_parts.append(f"{m['label'].split(' (')[0]}: {fmt(lv, m['unit'], per_capita)}")

                # fill pro stacked
                if is_stacked:
                    fill = "tozeroy" if mi == 0 else "tonexty"
                    stack_grp = "one"
                else:
                    fill = "tozeroy"
                    stack_grp = None

                fig.add_trace(go.Scatter(
                    x=yrs, y=y,
                    name=m["label"].split(" (")[0],
                    mode="lines",
                    line=dict(color=m["color"], width=1.8, shape="spline", smoothing=0.5),
                    fill=fill,
                    fillcolor=hex_rgba(m["color"], 0.25),
                    connectgaps=False,
                    stackgroup=stack_grp,
                    hovertemplate=(
                        f"<b>%{{x}}</b><br>"
                        f"{m['label'].split(' (')[0]}: %{{y:,.2f}} {m['unit']}"
                        f"{'<br><i>na osobu</i>' if per_capita else ''}"
                        "<extra></extra>"
                    ),
                ))

            if not has_any:
                col.empty()
                continue

            stat_str = " · ".join(stat_parts[:2])

            # ── layout kartičky ──────────────────────────────────────────
            fig.update_layout(
                height=185,
                margin=dict(l=0, r=4, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                hovermode="x unified",
                hoverlabel=dict(
                    bgcolor="#1a1f2e",
                    bordercolor="#2e3a55",
                    font=dict(color="#c8cfe0", size=11),
                ),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.04)",
                    gridwidth=1,
                    zeroline=False,
                    tickfont=dict(size=9, color="#3a4258"),
                    tickcolor="#1e2435",
                    linecolor="#1e2435",
                    dtick=15 if (yr1-yr0) > 40 else (10 if (yr1-yr0) > 20 else 5),
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.04)",
                    gridwidth=1,
                    zeroline=False,
                    rangemode="tozero",
                    tickfont=dict(size=9, color="#3a4258"),
                    tickcolor="#1e2435",
                    linecolor="#1e2435",
                    tickformat=",~g",
                ),
            )

            # ── render jako HTML kartička ─────────────────────────────────
            card_html = f"""
            <div class="card">
              <div class="card-header">
                <span class="card-title">{ctry['name']}</span>
                <span class="card-stat">{stat_str}</span>
              </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # dopln prázdné sloupce v poslední řadě
    for _ in range(n_cols - len(row)):
        cols[len(row) + _].empty()
