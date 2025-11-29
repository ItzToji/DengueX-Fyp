# dashboard_public.py
# Professional dengue charts: improved header + inferno calendar heatmap + top-3 months annotation
import streamlit as st
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parents[1]
PROC = ROOT / "data" / "processed"

st.set_page_config(layout="wide", page_title="Dengue Charts", page_icon="🦟")
px.defaults.template = "plotly_dark"

def read_processed():
    candidates = [
        PROC / "Dengue_data.csv",
        PROC / "dengue_data.csv",
        PROC / "monthly_dengue_2019_2024.csv",
        PROC / "weekly_provincial_dengue_2025.csv",
        PROC / "pakistan_dengue_kaggle.csv",
    ]
    for p in candidates:
        if p.exists():
            try:
                return pd.read_csv(p, low_memory=False)
            except Exception:
                continue
    return pd.DataFrame()

df_raw = read_processed()
if df_raw.empty:
    st.error("No processed CSV found in data/processed/. Add Dengue_data.csv or monthly/weekly CSVs.")
    st.stop()

df_raw.columns = df_raw.columns.str.strip().str.lower()

date_cols = [c for c in df_raw.columns if "date" in c or c in ("week","month","period","report_date","notification_date")]
if date_cols:
    df_raw["date"] = pd.to_datetime(df_raw[date_cols[0]], errors="coerce", dayfirst=True)
else:
    df_raw["date"] = pd.to_datetime(df_raw.iloc[:, 0], errors="coerce", dayfirst=True)

cases_cols = [c for c in df_raw.columns if any(k in c for k in ("case","cases","dengue_total","total"))]
if cases_cols:
    df_raw["cases"] = pd.to_numeric(df_raw[cases_cols[0]], errors="coerce").fillna(0).astype(int)
else:
    num_cols = [c for c in df_raw.columns if pd.api.types.is_numeric_dtype(df_raw[c])]
    if num_cols:
        sums = {c: df_raw[c].sum(skipna=True) for c in num_cols}
        chosen = max(sums, key=sums.get)
        df_raw["cases"] = pd.to_numeric(df_raw[chosen], errors="coerce").fillna(0).astype(int)
    else:
        df_raw["cases"] = 0

for c in ("city","district","province","adm2","adm_2","admin2","name"):
    if c in df_raw.columns:
        df_raw[c] = df_raw[c].astype(str).str.strip()

df = df_raw.drop_duplicates().copy()

# ---------- styling & header ----------
st.markdown("""
<style>
.header-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.brand {font-weight:700;font-size:18px}
.subtle {color:#9fb0be;font-size:13px}
.kpi-row {display:flex; gap:18px; align-items:center}
.kpi {background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:14px; border-radius:10px; min-width:180px}
.kpi .label{color:#aab7bf;font-size:12px}
.kpi .value{font-weight:800;font-size:20px}
</style>
""", unsafe_allow_html=True)

# header: minimal, professional (no "public" label)
st.markdown('<div class="header-row"><div><div class="brand">Pakistan Dengue Dashboard</div>', unsafe_allow_html=True)

# ---------- KPIs ----------
total = int(df["cases"].sum())
avg_week = 0
if "date" in df.columns and df["date"].notna().any():
    try:
        avg_week = int(df.set_index("date").resample("W")["cases"].sum().mean())
    except Exception:
        avg_week = 0

peak_value = 0
peak_month_str = ""
if "date" in df.columns and df["date"].notna().any():
    tmp = df.copy()
    tmp["month"] = tmp["date"].dt.to_period("M").dt.to_timestamp()
    agg = tmp.groupby("month", as_index=False)["cases"].sum()
    if not agg.empty:
        top = agg.sort_values("cases", ascending=False).head(1)
        peak_value = int(top["cases"].iloc[0])
        peak_month_str = pd.to_datetime(top["month"].iloc[0]).strftime("%Y-%m")

st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Total cases (all data)</div><div class="value">{total:,}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Average weekly cases</div><div class="value">{avg_week:,}</div></div>', unsafe_allow_html=True)
st.markdown(f'<div class="kpi"><div class="label">Peak month (cases)</div><div class="value">{peak_value:,}</div><div style="color:#9fb0be;margin-top:6px">{peak_month_str}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# ---------- Charts ----------
c1, c2 = st.columns(2)

with c1:
    st.markdown("**Weekly trend**")
    if "date" in df.columns and df["date"].notna().any():
        wk = df.set_index("date").resample("W")["cases"].sum().reset_index()
        fig_w = px.bar(wk, x="date", y="cases", labels={"date":"Week","cases":"Cases"}, height=420)
        fig_w.update_traces(marker=dict(opacity=0.9))
        fig_w.update_layout(margin=dict(t=12,l=0,r=0,b=0))
        st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("No parsable date to show weekly timeline.")

with c2:
    st.markdown("**Monthly detail**")
    if "date" in df.columns and df["date"].notna().any():
        m = df.copy()
        m["month"] = m["date"].dt.to_period("M").dt.to_timestamp()
        if "city" in m.columns and m["city"].notna().any():
            agg = m.groupby(["month","city"], as_index=False)["cases"].sum()
            fig_m = px.bar(agg, x="month", y="cases", color="city", labels={"month":"Month","cases":"Cases"}, height=420)
        elif "province" in m.columns and m["province"].notna().any():
            agg = m.groupby(["month","province"], as_index=False)["cases"].sum()
            fig_m = px.bar(agg, x="month", y="cases", color="province", labels={"month":"Month","cases":"Cases"}, height=420)
        else:
            agg = m.groupby("month", as_index=False)["cases"].sum()
            fig_m = px.bar(agg, x="month", y="cases", labels={"month":"Month","cases":"Cases"}, height=420)
        fig_m.update_traces(opacity=0.88)
        fig_m.update_layout(margin=dict(t=12,l=0,r=0,b=0))
        st.plotly_chart(fig_m, use_container_width=True)
    else:
        st.info("No parsable date to show monthly detail.")

st.markdown("---")

c3, c4 = st.columns(2)
with c3:
    st.markdown("**Yearly overview**")
    if "date" in df.columns and df["date"].notna().any():
        y = df.copy(); y["year"] = y["date"].dt.year
        if "city" in y.columns and y["city"].notna().any():
            agg_y = y.groupby(["year","city"], as_index=False)["cases"].sum()
            fig_y = px.area(agg_y, x="year", y="cases", color="city", labels={"year":"Year","cases":"Cases"}, height=420)
        elif "province" in y.columns and y["province"].notna().any():
            agg_y = y.groupby(["year","province"], as_index=False)["cases"].sum()
            fig_y = px.area(agg_y, x="year", y="cases", color="province", labels={"year":"Year","cases":"Cases"}, height=420)
        else:
            agg_y = y.groupby("year", as_index=False)["cases"].sum()
            fig_y = px.line(agg_y, x="year", y="cases", markers=True, labels={"year":"Year","cases":"Cases"}, height=420)
        fig_y.update_traces(opacity=0.75)
        fig_y.update_layout(margin=dict(t=12,l=0,r=0,b=0))
        st.plotly_chart(fig_y, use_container_width=True)
    else:
        st.info("No date to compute yearly aggregates.")

with c4:
    st.markdown("**Seasonality (monthly pattern by year)**")
    if "date" in df.columns and df["date"].notna().any():
        s = df.copy(); s["year"] = s["date"].dt.year; s["month"] = s["date"].dt.month
        agg_s = s.groupby(["year","month"], as_index=False)["cases"].sum()
        fig_s = px.line(agg_s, x="month", y="cases", color="year", markers=True, labels={"month":"Month (1=Jan)","cases":"Cases"}, height=420)
        fig_s.update_xaxes(tickmode="array", tickvals=list(range(1,13)), ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])
        fig_s.update_traces(opacity=0.9)
        fig_s.update_layout(margin=dict(t=12,l=0,r=0,b=0))
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("Monthly data required for seasonality chart.")

st.markdown("---")

# ---------- Monthly Calendar heatmap (non-zero months only) ----------
st.markdown("**Monthly Calendar Heatmap (timeline)**")
if "date" in df.columns and df["date"].notna().any():
    cal = df.copy()
    cal["year"] = cal["date"].dt.year
    cal["month"] = cal["date"].dt.month.astype(int)
    agg_cal = cal.groupby(["year","month"], as_index=False)["cases"].sum()

    if agg_cal.empty:
        st.info("No monthly counts available.")
    else:
        pivot = agg_cal.pivot(index="year", columns="month", values="cases").fillna(0).sort_index()
        # drop month columns that are all zero
        nonzero_cols = [c for c in pivot.columns if pivot[c].sum() > 0]
        pivot = pivot[nonzero_cols] if nonzero_cols else pivot.loc[:, []]
        # drop year rows that sum to zero
        pivot = pivot[pivot.sum(axis=1) > 0]

        if pivot.empty:
            st.info("Heatmap: no non-zero months to display.")
        else:
            matrix = pivot.values.astype(int)
            text_matrix = np.where(matrix > 0, matrix.astype(str), "")
            month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            x_labels = [month_names[m-1] for m in pivot.columns]

            # Top 3 hottest months (global)
            flat = agg_cal[agg_cal["cases"] > 0].copy()
            flat["ym"] = flat.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}", axis=1)
            top3 = flat.sort_values("cases", ascending=False).head(3)
            top3_list = [f"{row['ym']}: {int(row['cases']):,}" for _, row in top3.iterrows()]

            # heatmap (Inferno palette)
            fig_cal = go.Figure(data=go.Heatmap(
                z=matrix,
                x=x_labels,
                y=pivot.index.astype(str).tolist(),
                colorscale="Inferno",
                text=text_matrix,
                texttemplate="%{text}",
                hovertemplate="Year: %{y}<br>Month: %{x}<br>Cases: %{z}<extra></extra>",
                colorbar=dict(title="Cases")
            ))
            fig_cal.update_layout(height=420, margin=dict(t=8,l=0,r=0,b=0))
            fig_cal.update_yaxes(autorange="reversed")
            # render top3 annotation as markdown to the right of the chart
            col_heat, col_ctx = st.columns([4,1])
            with col_heat:
                st.plotly_chart(fig_cal, use_container_width=True)
            with col_ctx:
                st.markdown("**Top 3 months**")
                if top3_list:
                    for i, t in enumerate(top3_list, start=1):
                        st.markdown(f"{i}. {t}")
                else:
                    st.markdown("No cases recorded.")
else:
    st.info("Need valid dates to generate heatmap.")

st.markdown("---")
st.markdown("Chart notes: charts use processed CSV(s) from `data/processed`. Heatmap shows only months with non-zero counts.")
