import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from shapely.geometry import Point
import geopandas as gpd

st.set_page_config(layout="wide")
st.title("🗺️ GeoAI Mapper – Mineral Prospectivity Explorer with Explanation")

# Step 1: Load prediction results
@st.cache_data
def load_predictions():
    df = pd.read_csv("prediction_results.csv")
    return df

df = load_predictions()

# Step 2: Sidebar controls
st.sidebar.title("⚙️ Map Settings")
threshold = st.sidebar.slider("Minimum mineral potential", 0.0, 1.0, 0.5, 0.01)
view_mode = st.sidebar.radio("Map View Mode", ["Heatmap", "Circle Markers"])

filtered_df = df[df["mineral_potential"] >= threshold]
st.sidebar.markdown(f"**Filtered Points:** {len(filtered_df)}")

# Step 3: Base map setup
map_center = [df["lat"].mean(), df["lon"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

# Step 4: Add points
if view_mode == "Heatmap":
    heat_data = [
        [row["lat"], row["lon"], row["mineral_potential"]]
        for index, row in filtered_df.iterrows()
    ]
    if heat_data:
        HeatMap(heat_data, radius=8, blur=15, max_zoom=1).add_to(m)
else:
    for _, row in filtered_df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=4,
            fill=True,
            color="red",
            fill_opacity=row["mineral_potential"],
            popup=f"Potential: {row['mineral_potential']:.2f}"
        ).add_to(m)

# Step 5: Show the map and capture click
st.subheader("🗺️ Mineral Potential Map")
click_data = st_folium(m, width=1000, height=600)

# Step 6: Handle clicked point
if click_data and click_data["last_clicked"]:
    lat = click_data["last_clicked"]["lat"]
    lon = click_data["last_clicked"]["lng"]
    st.markdown("---")
    st.subheader("🔍 Selected Point Details")

    # Find nearest point
    df["distance"] = np.sqrt((df["lat"] - lat) ** 2 + (df["lon"] - lon) ** 2)
    nearest = df.loc[df["distance"].idxmin()]

    st.write(f"**Coordinates:** ({nearest['lat']:.5f}, {nearest['lon']:.5f})")
    st.write(f"**Mineral Potential Score:** {nearest['mineral_potential']:.3f}")
    st.write("**Geological Features:**")
    rock_type = nearest["lithologic"] if pd.notnull(nearest["lithologic"]) else "Unknown"

    st.write({
    "Rock Type": rock_type,
    "Distance to Fault (m)": nearest["fault_dist"],
    "Distance to Fold (m)": nearest["fold_dist"]
})


# Step 7: Expandable table view
with st.expander("📋 Show Filtered Data Table"):
    st.dataframe(
        filtered_df[["lat", "lon", "lithologic", "fault_dist", "fold_dist", "mineral_potential"]]
        .sort_values("mineral_potential", ascending=False),
        height=300
    )
