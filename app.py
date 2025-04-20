import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🗺️ GeoAI Mapper – Mineral Prospectivity Explorer")

# Step 1: Load prediction results
@st.cache_data
def load_predictions():
    return pd.read_csv("prediction_results.csv")

df = load_predictions()

# Step 2: Sidebar controls
st.sidebar.title("⚙️ Map Settings")

# Threshold slider
threshold = st.sidebar.slider("Minimum mineral potential", 0.0, 1.0, 0.5, 0.01)
filtered_df = df[df["mineral_potential"] >= threshold]
st.sidebar.markdown(f"**Filtered Points:** {len(filtered_df)}")

# View toggle: Heatmap or Circle Markers
view_mode = st.sidebar.radio("Map View Mode", ["Heatmap", "Circle Markers"])

# Step 3: Create the base map
map_center = [df["lat"].mean(), df["lon"].mean()]
m = folium.Map(location=map_center, zoom_start=6)

# Step 4: Add heatmap or markers
if view_mode == "Heatmap":
    heat_data = [
        [row["lat"], row["lon"], row["mineral_potential"]]
        for index, row in filtered_df.iterrows()
    ]
    if heat_data:
        HeatMap(heat_data, radius=8, blur=15, max_zoom=1).add_to(m)
    else:
        st.warning("No data points meet the selected threshold.")
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

# Step 5: Display the map
st.subheader("🗺️ Mineral Potential Map")
st_folium(m, width=1000, height=600)

# Step 6: Expandable data table
with st.expander("📋 Show Filtered Data Table"):
    st.dataframe(
        filtered_df[["lat", "lon", "lithologic", "fault_dist", "fold_dist", "mineral_potential"]]
        .sort_values("mineral_potential", ascending=False),
        height=300
    )
