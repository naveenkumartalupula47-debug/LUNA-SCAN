# LUNA-SCAN
AI-Based Lunar Landing Site &amp; Resource Analyzer
# 🌙 LUNA-SCAN

### AI-Based Lunar Landing Site & Resource Analyzer

LUNA-SCAN is a prototype application designed to analyze lunar terrain and identify potentially suitable landing locations using digital elevation data, terrain characteristics, and AI/ML-based scoring techniques.

The project combines terrain analysis, hazard detection, illumination estimation, and resource-proxy analysis into a single interactive dashboard.

---

## 🚀 Project Overview

Selecting a suitable landing location on the Moon requires analyzing several terrain-related factors such as:

- Terrain elevation
- Surface slope
- Potential hazardous depressions
- Illumination conditions
- Resource-related terrain indicators

LUNA-SCAN processes lunar Digital Elevation Model (DEM) data and converts these factors into interpretable safety and suitability scores.

> **Note:** LUNA-SCAN is an educational/hackathon prototype and is not intended to replace professional spacecraft landing-site analysis.

---

## ✨ Key Features

### 🗺️ Lunar Terrain Analysis
Analyzes lunar Digital Elevation Model (DEM) data to calculate terrain characteristics.

### ⛰️ Slope Analysis
Calculates terrain slope from elevation gradients and identifies areas with lower slope values that may be more suitable for landing.

### ⚠️ Hazard Detection
Uses terrain-depression analysis to highlight potentially hazardous regions.

### ☀️ Illumination Analysis
Provides an illumination proxy based on terrain orientation and a configurable solar direction.

### 🧪 Resource Analysis
Generates a resource-proxy score using terrain-related indicators such as elevation and slope.

### 📊 Landing-Site Scoring
Combines multiple factors into an overall site suitability score.

### 📍 Candidate Location Detection
Generates a ranked list of candidate landing locations with:

- Latitude
- Longitude
- Elevation
- Slope
- Suitability score

### 📈 Interactive Dashboard
Provides visual maps and metrics for:

- DEM / Elevation
- Suitable areas
- Hazard areas
- Landing safety
- Illumination
- Resource proxy

---

## 🧠 AI / ML Approach

The project uses terrain-derived features to support landing-site analysis.

The repository also contains a machine-learning model file:

`luna_ml_model.pkl`

The project includes:

- Feature extraction
- Terrain analysis
- Suitability scoring
- Machine-learning model integration
- Candidate-site ranking

The current prototype focuses primarily on DEM-based terrain analysis and scoring.

---

## 🏗️ System Workflow

```text
Lunar DEM Data
      ↓
Data Preprocessing
      ↓
Elevation & Terrain Analysis
      ↓
Slope Calculation
      ↓
Hazard Detection
      ↓
Illumination Analysis
      ↓
Resource-Proxy Analysis
      ↓
Landing-Site Scoring
      ↓
Candidate Location Ranking
      ↓
Interactive Dashboard
🛠️ Technologies Used
Python
Streamlit
NumPy
Pandas
Rasterio
Matplotlib
SciPy
Scikit-learn
Digital Elevation Model (DEM) Data
📁 Project Structure
LUNA-SCAN/
│
├── app.py
├── train_model.py
├── luna_ml_model.pkl
├── Presenti.ai - Presenti.html
├── README.md
└── requirements.txt
⚙️ Installation
1. Clone the repository
git clone https://github.com/naveenkumartalupula47-debug/LUNA-SCAN.git
2. Navigate to the project directory
cd LUNA-SCAN
3. Install dependencies
pip install -r requirements.txt

If requirements.txt is not available, install the required libraries manually:

pip install streamlit numpy pandas rasterio matplotlib scipy scikit-learn
4. Run the application
streamlit run app.py

The application will open in your web browser.

📊 Analysis Components
Component	Purpose
Elevation	Understand lunar terrain height
Slope	Identify relatively flatter terrain
Hazard Detection	Highlight potentially hazardous terrain depressions
Illumination Proxy	Estimate terrain illumination characteristics
Resource Proxy	Provide a terrain-based resource indicator
Overall Score	Combine multiple analysis factors
Candidate Ranking	Identify high-scoring locations
🌙 Why LUNA-SCAN?

Future lunar exploration may require efficient tools for analyzing large amounts of planetary terrain data.

LUNA-SCAN demonstrates how:

Geospatial Data + Python + AI/ML + Visualization

can be combined into an interactive planetary-analysis application.

🎯 Project Goals
Analyze lunar terrain using real DEM data
Demonstrate automated landing-site assessment
Visualize potentially suitable and hazardous areas
Rank candidate landing locations
Explore the use of AI/ML in planetary data analysis
Build an accessible prototype for educational and hackathon use
🔮 Future Improvements

Future versions could include:

Higher-resolution lunar datasets
More advanced lunar imagery analysis
Crater detection using computer vision
More scientifically detailed illumination modelling
Additional geological and resource datasets
Multi-temporal illumination analysis
Advanced machine-learning models
Interactive lunar map navigation
More accurate landing constraints
Integration with additional planetary datasets
👥 Project

LUNA-SCAN

AI-Based Lunar Landing Site & Resource Analyzer

Developed as a hackathon / academic prototype exploring AI/ML applications in lunar terrain analysis.

⚠️ Disclaimer

LUNA-SCAN is a research and educational prototype.

Its suitability scores and candidate locations are generated from the implemented terrain-analysis methodology and should not be interpreted as certified spacecraft landing recommendations.

⭐ Acknowledgements

The project uses publicly available scientific/terrain data and open-source Python technologies for analysis and visualization.

🌙 LUNA-SCAN

Analyze. Visualize. Discover.
requirements.txt
streamlit
numpy
pandas
rasterio
matplotlib
scipy
scikit-learn
