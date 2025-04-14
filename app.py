import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from shapely.geometry import Point

st.set_page_config(layout="wide")

st.title("🗺️ GeoAI Mapper – Mineral Prospectivity Viewer")

# Step 1: Load prediction results
uploaded_file = st.file_uploader("Upload prediction_results.csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Optional check
    if "mineral_potential" not in df.columns:
        st.error("CSV must contain a 'mineral_potential' column.")
    else:
        st.success("Data loaded successfully!")
        
        # Ask for lat/lon input if not in CSV
        if "lon" not in df.columns or "lat" not in df.columns:
            st.warning("Latitude/Longitude columns not found. Generating synthetic geometry...")
            # Fake lat/lon assuming you're in UTM or projected CRS (for demo)
            df["lon"] = range(len(df))
            df["lat"] = range(len(df))

        # Step 2: Filter based on probability
        threshold = st.slider("Select probability threshold", 0.0, 1.0, 0.5, 0.01)
        filtered_df = df[df["mineral_potential"] >= threshold]

        st.markdown(f"**Filtered Points:** {len(filtered_df)}")

        # Step 3: Show table
        st.dataframe(filtered_df[["lithologic", "fault_dist", "fold_dist", "mineral_potential"]].sort_values("mineral_potential", ascending=False))

        # Step 4: Create map with Folium
        m = folium.Map(location=[filtered_df["lat"].mean(), filtered_df["lon"].mean()], zoom_start=6)
        
        # Add points
        for _, row in filtered_df.iterrows():
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=4,
                fill=True,
                color="red",
                fill_opacity=row["mineral_potential"],
                popup=f"Score: {row['mineral_potential']:.2f}"
            ).add_to(m)

        # Step 5: Show map in Streamlit
        st_folium(m, width=900, height=600)
