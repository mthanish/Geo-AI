import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# 1. Load geological layers
lithology = gpd.read_file("lithology.geojson")
faults = gpd.read_file("faults.geojson")
folds = gpd.read_file("folds.geojson")

print("Layers loaded successfully.")

# 2. Generate grid points across the region
minx, miny, maxx, maxy = lithology.total_bounds
spacing = 0.005  # ~500m in degrees

points = []
for x in np.arange(minx, maxx, spacing):
    for y in np.arange(miny, maxy, spacing):
        points.append(Point(x, y))

grid = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
print(f"Generated {len(grid)} grid points.")

# 3. Add lithology info
if 'lithologic' in lithology.columns:
    grid = gpd.sjoin(grid, lithology[["geometry", "lithologic"]], how="left", predicate="within")
else:
    print("Error: 'lithologic' column not found in lithology file.")
    exit()

# 4. Reproject all layers to UTM for accurate distance calculation
projected_crs = "EPSG:32643"
grid = grid.to_crs(projected_crs)
faults = faults.to_crs(projected_crs)
folds = folds.to_crs(projected_crs)

# 5. Calculate distances
grid["fault_dist"] = grid.geometry.apply(lambda x: faults.distance(x).min())
grid["fold_dist"] = grid.geometry.apply(lambda x: folds.distance(x).min())

# 6. Simulate labels (1% mineralized)
grid["label"] = 0
grid.loc[grid.sample(frac=0.01).index, "label"] = 1

# 7. Encode lithology
if grid["lithologic"].dtype == object:
    le = LabelEncoder()
    grid["lithologic_encoded"] = le.fit_transform(grid["lithologic"])
else:
    grid["lithologic_encoded"] = grid["lithologic"]

# 8. Train Random Forest model (for demo)
features = ["lithologic_encoded", "fault_dist", "fold_dist"]
target = "label"
X = grid[features]
y = grid[target]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

grid["mineral_potential"] = model.predict_proba(X)[:, 1]

# 9. Convert back to lat/lon and add to DataFrame
grid = grid.to_crs("EPSG:4326")
grid["lat"] = grid.geometry.y
grid["lon"] = grid.geometry.x

# 10. Save as prediction_results.csv
final_cols = ["lat", "lon", "lithologic", "fault_dist", "fold_dist", "label", "lithologic_encoded", "mineral_potential"]
grid[final_cols].to_csv("prediction_results.csv", index=False)

print("Saved final file: prediction_results.csv")
print("Feature engineering and model training completed successfully.")
