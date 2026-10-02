import rasterio
import numpy as np
from scipy.ndimage import sobel
from sklearn.ensemble import RandomForestClassifier

# Real lunar DEM
dem_file = "MOON_LRO_NAC_DEM_89S210E_4mp.tif"

with rasterio.open(dem_file) as src:
    elevation = src.read(1).astype(np.float64)
    transform = src.transform
    

print("DEM loaded successfully")

# Calculate terrain slope safely
res_x = abs(transform.a)
res_y = abs(transform.e)

dy, dx = np.gradient(elevation, res_y, res_x)

slope = np.degrees(np.arctan(np.sqrt(dx**2 + dy**2)))

slope = np.nan_to_num(slope, nan=0.0, posinf=0.0, neginf=0.0)


print("Slope calculated successfully")
print("Average slope:", np.mean(slope))

# Create labels
flat_slope = slope.ravel()
labels = (flat_slope <= 7).astype(int)

print("Training labels created")

# Select training samples
rng = np.random.default_rng(42)

indices = rng.choice(
    len(flat_slope),
    size=min(20000, len(flat_slope)),
    replace=False
)

X = flat_slope[indices].reshape(-1, 1)
y = labels[indices]

print("Training data ready")
print("Samples:", len(X))

# Train ML model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

print("ML model trained successfully")

# Test prediction
test_slope = np.array([
    [4],
    [9],
    [15]
])

predictions = model.predict(test_slope)

print("Test slopes:", test_slope.ravel())
print("Predictions:", predictions)
import pickle

with open("luna_ml_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("ML model saved successfully")