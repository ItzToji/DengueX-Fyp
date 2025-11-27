import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px

ROOT = Path(__file__).parents[1]
FILES = [
    ROOT / "data" / "processed" / "Dengue_data.csv",
    ROOT / "data" / "processed" / "pakistan_dengue_kaggle.csv",
]

def read_standard(p):
    df = pd.read_csv(p, low_memory=False)
    df.columns = df.columns.str.strip().str.lower()
    rename = {}
    for k in ("date","calendar_start_date","report_date","notification_date","reporting_date"):
        if k in df.columns and "date" not in rename.values(): rename[k] = "date"
    for k in ("dengue_total","cases","case_count","new_cases","total_cases"):
        if k in df.columns and "cases" not in rename.values(): rename[k] = "cases"
    for k in ("adm_2_name","district","district_name","admin2"):
        if k in df.columns and "district" not in rename.values(): rename[k] = "district"
    for k in ("adm_1_name","city","city_name","province"):
        if k in df.columns and "city" not in rename.values(): rename[k] = "city"
    for k in ("latitude","lat","y"):
        if k in df.columns and "lat" not in rename.values(): rename[k] = "lat"
    for k in ("longitude","lon","lng","x"):
        if k in df.columns and "lon" not in rename.values(): rename[k] = "lon"
    df = df.rename(columns={k:v for k,v in rename.items()})
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
    elif "year" in df.columns:
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01", errors="coerce")
    df["cases"] = pd.to_numeric(df.get("cases", 0), errors="coerce").fillna(0).astype(int)
    df["lat"] = pd.to_numeric(df.get("lat", np.nan), errors="coerce")
    df["lon"] = pd.to_numeric(df.get("lon", np.nan), errors="coerce")
    df["city"] = df.get("city", pd.NA).astype("string").str.strip()
    df["district"] = df.get("district", pd.NA).astype("string").str.strip()
    return df

frames = [read_standard(p) for p in FILES if p.exists()]
if not frames:
    st.set_page_config(layout="wide", page_title="Dengue Analytics")
    st.error("Processed files not found in data/processed/")
    st.stop()

df = pd.concat(frames, ignore_index=True, sort=False)
df = df[df["date"].notna()]
df = df.drop_duplicates(subset=["date","city","district","cases","lat","lon"])
df = df.sort_values("date")

st.set_page_config(layout="wide", page_title="Dengue Analytics — Islamabad & Rawalpindi", page_icon="🦟")

st.markdown(
    """
    <style>
    :root{
      --bg:#0b1116; --panel:#0f1720; --muted:#9fb0be; --accent1:#07a6d6; --accent2:#0e4b66;
      --glass: rgba(255,255,255,0.03);
    }
    .app-body { background:var(--bg); color:#e6eef6; padding:12px 18px; }
    .header {
      display:flex;align-items:center;justify-content:space-between;
      background: linear-gradient(90deg,var(--accent1),var(--accent2));
      padding:12px 18px;border-radius:12px;color:white;box-shadow:0 8px 30px rgba(2,6,23,0.6);
    }
    .brand {display:flex;gap:14px;align-items:center}
    .logo {width:56px;height:56px;border-radius:10px;background:rgba(255,255,255,0.06);display:flex;align-items:center;justify-content:center}
    .title {font-size:20px;font-weight:700;margin:0}
    .subtitle {font-size:12px;opacity:0.92;margin-top:2px}
    .controls {display:flex;gap:12px;align-items:center}
    .control {background:var(--panel);padding:8px 12px;border-radius:10px;color:var(--muted);font-size:14px}
    .kpi-row{display:flex;gap:12px;margin-top:14px}
    .kpi{flex:1;padding:14px;border-radius:10px;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));box-shadow:0 6px 18px rgba(2,6,23,0.6)}
    .kpi .label{color:var(--muted);font-size:12px}
    .kpi .value{font-size:28px;font-weight:700;margin-top:6px}
    .section{margin-top:22px}
    .small{color:var(--muted);font-size:13px}
    /* minimize Streamlit widget footprint */
    .stNumberInput > div { padding: 0; }
    .stNumberInput label { color: var(--muted); font-size:12px; margin-bottom:4px; display:block; }
    .stSelectbox > div { padding: 0; }
    .stDateInput > div { padding: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

min_date, max_date = df["date"].min().date(), df["date"].max().date()

st.markdown(f'<div class="header"><div class="brand"><div class="logo">🦟</div><div><div class="title">Dengue Analytics</div><div class="subtitle">Islamabad & Rawalpindi — 2020–2024</div></div></div>'
            f'<div class="controls"><div class="control small">Data: {min_date} → {max_date}</div></div></div>', unsafe_allow_html=True)

with st.container():
    dr = st.date_input("", [min_date, max_date], key="date_range")
    cities = sorted(df["city"].dropna().unique())
    sel = st.multiselect("", options=cities, default=cities, key="cities", help="Filter cities — select none to show all")
    df_f = df.copy()
    dr0, dr1 = pd.to_datetime(dr[0]), pd.to_datetime(dr[1])
    if sel:
        df_f = df_f[(df_f["date"] >= dr0) & (df_f["date"] <= dr1) & (df_f["city"].isin(sel))]
    else:
        df_f = df_f[(df_f["date"] >= dr0) & (df_f["date"] <= dr1)]

total = int(df_f["cases"].sum()) if not df_f.empty else 0
weekly = df_f.set_index("date").resample("W")["cases"].sum()
avgw = int(weekly.mean()) if not weekly.empty else 0
peak_row = df_f.groupby("date")["cases"].sum().reset_index().sort_values("cases", ascending=False).head(1)
peak_txt = "N/A" if peak_row.empty else f"{peak_row['date'].dt.date.iloc[0]} ({int(peak_row['cases'].iloc[0])})"

st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Total cases (selected)</div><div class="value">{total:,}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Avg weekly cases</div><div class="value">{avgw:,}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Peak single day</div><div class="value">{peak_txt}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><div style="display:flex;align-items:center;justify-content:space-between"><div style="font-size:18px;font-weight:700;color:#eaf6ff">Seasonality</div><div class="small">Monthly trend (click legend to toggle cities)</div></div></div>', unsafe_allow_html=True)

if not df_f.empty:
    tmp = df_f.copy()
    tmp["month"] = tmp["date"].dt.month
    monthly_city = tmp.groupby(["month", "city"], as_index=False)["cases"].sum()
    monthly_city["month_name"] = monthly_city["month"].map(lambda m: pd.Timestamp(2020, m, 1).strftime("%b"))
    fig_season = px.line(monthly_city, x="month", y="cases", color="city", markers=True, labels={"month":"Month","cases":"Cases"}, template="plotly_dark", height=380)
    fig_season.update_layout(xaxis=dict(tickmode="array", tickvals=list(range(1,13)), ticktext=[pd.Timestamp(2020,m,1).strftime("%b") for m in range(1,13)]), legend_title_text="City", margin=dict(t=8,l=0,r=0,b=0))
    st.plotly_chart(fig_season, use_container_width=True)
else:
    st.info("No data for seasonality chart.")

st.markdown('<div class="section" style="display:flex;align-items:center;justify-content:space-between"><div style="font-size:18px;font-weight:700;color:#eaf6ff">Map — affected areas</div>'
            '<div class="small">Choose view: Points / Clusters / Density</div></div>', unsafe_allow_html=True)

map_mode = st.selectbox("", ["Points", "Clusters", "Density (heatmap)"], index=0, key="map_mode")
# replaced sliders with compact numeric inputs to remove long slider bars
point_scale = st.number_input("Point scale (multiplier)", min_value=1, max_value=20, value=5, step=1, key="point_scale")
opacity_pct = st.number_input("Opacity (%)", min_value=20, max_value=100, value=88, step=1, key="opacity_pct")
opacity = opacity_pct / 100.0

if not df_f.empty and df_f[["lat","lon"]].notna().any().any():
    pts = df_f.groupby(["lat","lon","city","district"], as_index=False)["cases"].sum()
    pts = pts[pts["cases"] > 0].copy()
    center = {"lat": float(pts["lat"].mean()), "lon": float(pts["lon"].mean())}

    if map_mode == "Points":
        pts["size"] = (np.sqrt(pts["cases"]) * point_scale).clip(4, 60)
        pts["cases_bin"] = pd.qcut(pts["cases"].clip(lower=1), q=4, labels=["Low","Medium","High","Very high"])
        color_map = {"Low":"#7fc97f","Medium":"#fdc086","High":"#fb8072","Very high":"#b15928"}
        fig_map = px.scatter_mapbox(
            pts, lat="lat", lon="lon", color="cases_bin", size="size",
            hover_name="city", hover_data={"district":True, "cases":True},
            color_discrete_map=color_map, center=center, zoom=10, height=620, template="plotly_dark"
        )
        fig_map.update_traces(marker=dict(opacity=opacity))
        fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"t":6,"b":6,"l":6,"r":6})
        st.plotly_chart(fig_map, use_container_width=True)

    elif map_mode == "Clusters":
        grid_deg = st.number_input("Cluster rounding precision (decimal places)", min_value=0, max_value=6, value=3, step=1, key="grid_deg")
        pts["lat_r"] = pts["lat"].round(grid_deg)
        pts["lon_r"] = pts["lon"].round(grid_deg)
        cl = pts.groupby(["lat_r","lon_r"], as_index=False).agg({"cases":"sum","city": lambda s: ", ".join(sorted(set([str(x) for x in s if pd.notna(x)]) )[:3]), "lat":"mean","lon":"mean"})
        cl["size"] = (np.sqrt(cl["cases"]) * point_scale * 1.4).clip(6, 120)
        cl["label"] = cl["city"] + " (" + cl["cases"].astype(int).astype(str) + ")"
        fig_map = px.scatter_mapbox(cl, lat="lat", lon="lon", size="size", size_max=120, color="cases", hover_name="label", hover_data={"cases":True}, color_continuous_scale="Turbo", center=center, zoom=10, height=620, template="plotly_dark")
        fig_map.update_traces(marker=dict(opacity=opacity))
        fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"t":6,"b":6,"l":6,"r":6}, coloraxis_colorbar=dict(title="Cases"))
        st.plotly_chart(fig_map, use_container_width=True)

    else:
        radius = st.number_input("Heat radius (px)", min_value=5, max_value=80, value=24, step=1, key="heat_radius")
        fig_density = px.density_mapbox(pts, lat="lat", lon="lon", z="cases", radius=radius, center=center, zoom=10, mapbox_style="carto-darkmatter", height=620, color_continuous_scale="YlOrRd")
        fig_density.update_layout(margin={"t":6,"b":6,"l":6,"r":6}, template="plotly_dark")
        st.plotly_chart(fig_density, use_container_width=True)

else:
    st.info("No geolocation data available for map.")
