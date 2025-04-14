import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🗺️ GeoAI Mapper – Mineral Prospectivity Viewer")

# Step 1: Load prediction results from file (no upload)
@st.cache_data
def load_data():
    df = pd.read_csv("prediction_results.csv")
    return df

df = load_data()

# Step 2: Check required columns
required_cols = {"lat", "lon", "mineral_potential"}
if not required_cols.issubset(df.columns):
    st.error("Missing required columns in prediction_results.csv.")
    st.stop()

# Step 3: Threshold slider
threshold = st.slider("Select probability threshold", 0.0, 1.0, 0.5, 0.01)
filtered_df = df[df["mineral_potential"] >= threshold]
st.markdown(f"**Filtered Locations Above Threshold:** {len(filtered_df)}")

# Step 4: Show data table
st.dataframe(filtered_df[["lat", "lon", "lithologic", "fault_dist", "fold_dist", "mineral_potential"]]
             .sort_values("mineral_potential", ascending=False))

# Step 5: Create map
m = folium.Map(location=[df["lat"].mean(), df["lon"].mean()], zoom_start=6)

# Add mineral potential points
for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=4,
        fill=True,
        color="red",
        fill_opacity=row["mineral_potential"],
        popup=f"Potential: {row['mineral_potential']:.2f}"
    ).add_to(m)

# Step 6: Display map
st_folium(m, width=900, height=600)
