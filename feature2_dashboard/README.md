                                                           Feature-2: Dengue Analytics Dashboard 

# 📌 Overview

Feature-2 of the DengueX Final Year Project is a Dengue Analytics Dashboard designed to visualize dengue case trends, hotspots, and comparisons for Islamabad and Rawalpindi.
This dashboard processes epidemiological data, merges it with geospatial boundaries, and presents interactive visual insights for public-health decision support.

# 🎯 Objectives

Provide a visual overview of dengue activity (2020–2024).

Compare Islamabad vs Rawalpindi case trends.

Display geographic hotspots using district-level maps.

Integrate official surveillance data (NIH weekly bulletins).

Support interactive exploration using filters and charts.

# 📊 Key Features

1. Time-Series Analysis

Daily/weekly dengue cases

Moving averages

Year-wise comparison

Trendlines for outbreak detection

2. Geospatial Mapping

District-level choropleth maps

Islamabad + Rawalpindi focus

Hover-based case summaries

3. Data Integration

Kaggle Pakistan dengue dataset

NIH Weekly Epidemiological Reports (PDF)

GADM Pakistan District GeoJSON for mapping

4. Filtering & Interactivity

Date range selection

City/district filters

Exportable graphs and tables

# 🗂️ Data Sources

Pakistan Dengue Dataset (CSV) — case trends

NIH IDSR Weekly Bulletin (PDF) — official weekly numbers

GADM Pakistan District Boundaries (GeoJSON) — mapping layers

🛠️ Technology Stack

Python (Pandas, GeoPandas)

Streamlit (dashboard interface)

Plotly / Folium (visualizations)

Camelot / Tabula (PDF table extraction)

# ▶️ How It Works

Raw datasets (CSV, PDF, GeoJSON) are placed in data/raw/.

Cleaning & preprocessing scripts transform them into unified formats.

Final datasets are stored in data/processed/.

Streamlit reads processed data and renders interactive visualizations.

The dashboard is embedded into the main DengueX website.

# 📦 Output

The dashboard produces:

Cleaned dengue case dataset (2020–2024)

District-level geospatial files

Interactive dashboard (Streamlit)

Summary reports & visual insights

# 👤 Developed By

Feature-2 Lead: Your Name
Role: Data Collection • Cleaning • Analysis • Dashboard Development