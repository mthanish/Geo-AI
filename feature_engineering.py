import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load geological layers
lithology = gpd.read_file("lithology.geojson")
faults = gpd.read_file("faults.geojson")
folds = gpd.read_file("folds.geojson")

print("Layers loaded successfully.")

# 2. Generate a grid of points across the region
minx, miny, maxx, maxy = lithology.total_bounds
spacing = 0.005  # degrees ~500m spacing

points = []
for x in np.arange(minx, maxx, spacing):
    for y in np.arange(miny, maxy, spacing):
        points.append(Point(x, y))

grid = gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")
print(f"Generated {len(grid)} grid points.")

# 3. Add rock type (lithology) to each grid point
grid = gpd.sjoin(grid, lithology[["geometry", "lithologic"]], how="left", predicate="within")

# 4. Calculate distance to nearest fault and fold
grid["fault_dist"] = grid.geometry.apply(lambda x: faults.distance(x).min())
grid["fold_dist"] = grid.geometry.apply(lambda x: folds.distance(x).min())

# 5. Simulate mineral occurrence labels for demo
grid["label"] = 0
grid.loc[grid.sample(frac=0.01).index, "label"] = 1

# 6. Save as CSV
grid.drop(columns="geometry").to_csv("features.csv", index=False)
print("Feature table saved as features.csv")

# 7. Plot distance to faults
grid.plot(column="fault_dist", cmap="viridis", markersize=1, legend=True)
plt.title("Distance to Faults")
plt.show()
