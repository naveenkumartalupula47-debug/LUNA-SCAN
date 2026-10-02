

import rasterio
import numpy as np
import pandas as pd
import streamlit as st
import pickle
import matplotlib.pyplot as plt
from rasterio.transform import xy
from rasterio.warp import transform
from scipy.ndimage import gaussian_filter

# -------------------------------------------------
# PAGE SETUP
# -------------------------------------------------

st.set_page_config(
    page_title=("LUNA-SCAN"),
    page_icon="🌙",
    layout="wide"
)

st.title("🌙 LUNA-SCAN")
st.subheader("AI-Based Lunar Landing Site & Resource Analyzer")
st.caption("Real Lunar DEM Based Terrain Analysis")

dem_file = "MOON_LRO_NAC_DEM_89S210E_4mp.tif"
with open("luna_ml_model.pkl", "rb") as f:
    ml_model = pickle.load(f)

try:

    # -------------------------------------------------
    # 1. READ REAL LUNAR DEM
    # -------------------------------------------------

    with rasterio.open(dem_file) as src:




        scale = 20

        new_height = max(1, src.height // scale)
        new_width = max(1, src.width // scale)

        elevation = src.read(
            1,
            out_shape=(new_height, new_width),
            masked=True
        ).astype("float32")

        elevation = elevation.filled(np.nan)

        new_transform = src.transform * src.transform.scale(
            src.width / new_width,
            src.height / new_height
        )

        original_crs = src.crs

    valid_elevation = elevation[np.isfinite(elevation)]

    if len(valid_elevation) == 0:
        st.error("No valid elevation data found.")
        st.stop()

    avg_height = float(np.mean(valid_elevation))
    max_height = float(np.max(valid_elevation))
    min_height = float(np.min(valid_elevation))

    # -------------------------------------------------
    # 2. AUTOMATIC SLOPE ANALYSIS
    # -------------------------------------------------

    x_resolution = abs(new_transform.a)
    y_resolution = abs(new_transform.e)

    dy, dx = np.gradient(
        elevation,
        y_resolution,
        x_resolution
    )

    slope = np.degrees(
        np.arctan(
            np.sqrt(dx ** 2 + dy ** 2)
        )
    )

    valid_slope = slope[np.isfinite(slope)]

    avg_slope = float(np.mean(valid_slope))

    slope_threshold = np.percentile(
        valid_slope,
        20
    )

    safe_mask = (
        np.isfinite(slope)
        & (slope <= slope_threshold)
    )

    safe_count = int(np.sum(safe_mask))
    total_valid = int(np.sum(np.isfinite(slope)))

    # -------------------------------------------------
    # 3. CRATER / HAZARD SCREENING
    # -------------------------------------------------

    smooth_dem = gaussian_filter(
        elevation,
        sigma=3
    )

    depression = smooth_dem - elevation

    valid_depression = depression[
        np.isfinite(depression)
    ]

    depression_threshold = np.percentile(
        valid_depression,
        90
    )

    hazard_mask = (
        np.isfinite(depression)
        & (depression >= depression_threshold)
    )

    hazard_count = int(np.sum(hazard_mask))

    # -------------------------------------------------
    # 4. LANDING SAFETY SCORE
    # -------------------------------------------------

    max_slope = np.nanmax(slope)

    if max_slope > 0:
        slope_score = np.clip(
            100 - (slope / max_slope * 100),
            0,
            100
        )
    else:
        slope_score = np.full_like(
            slope,
            100,
            dtype=float
        )

    hazard_penalty = np.where(
        hazard_mask,
        0,
        100
    )

    landing_safety = (
        slope_score * 0.6
        + hazard_penalty * 0.4
    )

    valid_safety = landing_safety[
        np.isfinite(landing_safety)
    ]

    average_safety = float(
        np.mean(valid_safety)
    )

    # -------------------------------------------------
    # 5. TERRAIN ILLUMINATION PROXY
    # -------------------------------------------------

    aspect = np.degrees(
        np.arctan2(-dy, dx)
    )

    aspect = (aspect + 360) % 360

    solar_direction = 180

    angle_difference = np.abs(
        aspect - solar_direction
    )

    angle_difference = np.minimum(
        angle_difference,
        360 - angle_difference
    )

    illumination_score = (
        np.cos(np.radians(angle_difference)) + 1
    ) * 50

    illumination_score = np.clip(
        illumination_score,
        0,
        100
    )

    valid_illumination = illumination_score[
        np.isfinite(illumination_score)
    ]

    average_illumination = float(
        np.mean(valid_illumination)
    )

    # -------------------------------------------------
    # 6. TERRAIN RESOURCE POTENTIAL PROXY
    # -------------------------------------------------

    elevation_range = (
        np.nanmax(elevation)
        - np.nanmin(elevation)
    )

    if elevation_range > 0:
        elevation_score = (
            100
            - (
                (elevation - np.nanmin(elevation))
                / elevation_range
                * 100
            )
        )
    else:
        elevation_score = np.full_like(
            elevation,
            50,
            dtype=float
        )

    resource_potential = (
        elevation_score * 0.4
        + slope_score * 0.6
    )

    resource_potential = np.clip(
        resource_potential,
        0,
        100
    )

    valid_resource = resource_potential[
        np.isfinite(resource_potential)
    ]

    average_resource = float(
        np.mean(valid_resource)
    )

    # -------------------------------------------------
    # 7. FINAL LUNA-SCAN SCORE
    # -------------------------------------------------

    final_score_map = (
        landing_safety * 0.40
        + illumination_score * 0.20
        + resource_potential * 0.20
        + slope_score * 0.20
    )

    valid_final = final_score_map[
        np.isfinite(final_score_map)
    ]

    overall_score = float(
        np.mean(valid_final)
    )

    # -------------------------------------------------
    # 8. TOP CANDIDATE LANDING SITES
    # -------------------------------------------------

    candidate_rows, candidate_cols = np.where(
        np.isfinite(final_score_map)
    )

    candidate_scores = final_score_map[
        candidate_rows,
        candidate_cols
    ]

    top_n = min(
        5,
        len(candidate_scores)
    )

    top_indices = np.argsort(
        candidate_scores
    )[-top_n:][::-1]

    top_candidates = []

    for rank, idx in enumerate(
        top_indices,
        start=1
    ):

        row = int(candidate_rows[idx])
        col = int(candidate_cols[idx])

        x, y = xy(
            new_transform,
            row,
            col,
            offset="center"
        )

        try:

            lon, lat = transform(
                original_crs,
                "EPSG:4326",
                [x],
                [y]
            )

            latitude = float(lat[0])
            longitude = float(lon[0])

        except Exception:

            latitude = float(y)
            longitude = float(x)

        top_candidates.append({
            "Rank": rank,
            "Latitude": round(latitude, 6),
            "Longitude": round(longitude, 6),
            "Suitability Score": round(
                float(final_score_map[row, col]),
                2
            ),
            "Slope (°)": round(
                float(slope[row, col]),
                2
            ),
            "Elevation": round(
                float(elevation[row, col]),
                2
            )
        })

    candidate_table = pd.DataFrame(
        top_candidates
    )

    # =================================================
    # DASHBOARD
    # =================================================

    st.divider()
    st.subheader("📊 LUNA-SCAN Mission Dashboard")

    dash1, dash2, dash3, dash4 = st.columns(4)

    dash1.metric(
        "🤖 Overall Score",
        f"{overall_score:.1f}/100"
    )

    dash2.metric(
        "🛰️ Landing Safety",
        f"{average_safety:.1f}/100"
    )

    dash3.metric(
        "☀️ Illumination Proxy",
        f"{average_illumination:.1f}/100"
    )

    dash4.metric(
        "💧 Resource Proxy",
        f"{average_resource:.1f}/100"
    )

    st.divider()

    # -------------------------------------------------
    # REAL MOON DEM
    # -------------------------------------------------

    st.subheader("🌙 Real Moon DEM Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Elevation",
        f"{avg_height:.2f}"
    )

    col2.metric(
        "Maximum Elevation",
        f"{max_height:.2f}"
    )

    col3.metric(
        "Minimum Elevation",
        f"{min_height:.2f}"
    )

    # -------------------------------------------------
    # TERRAIN ANALYSIS
    # -------------------------------------------------

    st.subheader("⛰️ Automatic Terrain Analysis")

    t1, t2, t3 = st.columns(3)

    t1.metric(
        "Average Surface Slope",
        f"{avg_slope:.2f}°"
    )

    t2.metric(
        "Suitable Terrain Cells",
        f"{safe_count:,}"
    )

    t3.metric(
        "Slope Threshold",
        f"{slope_threshold:.2f}°"
    )

    st.write(
        f"Valid terrain cells analysed: {total_valid:,}"
    )

    # -------------------------------------------------
    # REAL LUNAR TERRAIN MAP
    # -------------------------------------------------

    st.subheader("🗺️ Real Lunar Terrain Map")

    fig, ax = plt.subplots(
        figsize=(10, 6)
    )

    image = ax.imshow(
        elevation,
        cmap="gray"
    )

    ax.set_title(
        "Lunar Digital Elevation Model"
    )

    ax.set_xlabel("DEM X")
    ax.set_ylabel("DEM Y")

    plt.colorbar(
        image,
        ax=ax,
        label="Elevation"
    )

    st.pyplot(
        fig,
        clear_figure=True
    )

    # -------------------------------------------------
    # SUITABLE TERRAIN MAP
    # -------------------------------------------------

    st.subheader(
        "🟢 Automatically Detected Suitable Areas"
    )

    fig2, ax2 = plt.subplots(
        figsize=(10, 6)
    )

    ax2.imshow(
        elevation,
        cmap="gray"
    )

    suitable_display = np.where(
        safe_mask,
        1,
        np.nan
    )

    ax2.imshow(
        suitable_display,
        cmap="Greens",
        alpha=0.6
    )

    ax2.set_title(
        "Potentially Suitable Terrain Based on DEM Slope"
    )

    ax2.set_xlabel("DEM X")
    ax2.set_ylabel("DEM Y")

    st.pyplot(
        fig2,
        clear_figure=True
    )

    # -------------------------------------------------
    # HAZARD ANALYSIS
    # -------------------------------------------------

    st.subheader(
        "⚠️ Lunar Crater / Hazard Screening"
    )

    st.metric(
        "Potential Hazard Cells",
        f"{hazard_count:,}"
    )

    st.write(
        f"Depression threshold used: "
        f"{depression_threshold:.2f}"
    )

    fig3, ax3 = plt.subplots(
        figsize=(10, 6)
    )

    ax3.imshow(
        elevation,
        cmap="gray"
    )

    hazard_display = np.where(
        hazard_mask,
        1,
        np.nan
    )

    ax3.imshow(
        hazard_display,
        cmap="Reds",
        alpha=0.65
    )

    ax3.set_title(
        "Potential Lunar Depression / Crater Hazard Areas"
    )

    ax3.set_xlabel("DEM X")
    ax3.set_ylabel("DEM Y")

    st.pyplot(
        fig3,
        clear_figure=True
    )

    st.info(
        "Red regions represent terrain depressions "
        "identified from the real lunar DEM. "
        "They are potential hazard areas and require "
        "additional scientific validation."
    )

    # -------------------------------------------------
    # LANDING SAFETY
    # -------------------------------------------------

    st.subheader(
        "🛰️ Automatic Landing Safety Analysis"
    )

    if average_safety >= 75:
        st.success(
            f"🟢 High terrain suitability detected — "
            f"{average_safety:.1f}/100"
        )
    elif average_safety >= 50:
        st.warning(
            f"🟡 Moderate terrain suitability — "
            f"{average_safety:.1f}/100"
        )
    else:
        st.error(
            f"🔴 Lower terrain suitability — "
            f"{average_safety:.1f}/100"
        )

    fig4, ax4 = plt.subplots(
        figsize=(10, 6)
    )

    safety_plot = ax4.imshow(
        landing_safety,
        cmap="viridis"
    )

    ax4.set_title(
        "Automatic Lunar Landing Safety Map"
    )

    ax4.set_xlabel("DEM X")
    ax4.set_ylabel("DEM Y")

    plt.colorbar(
        safety_plot,
        ax=ax4,
        label="Safety Score"
    )

    st.pyplot(
        fig4,
        clear_figure=True
    )

    # -------------------------------------------------
    # ILLUMINATION
    # -------------------------------------------------

    st.subheader(
        "☀️ Lunar Illumination Analysis"
    )

    st.metric(
        "Terrain Illumination Proxy",
        f"{average_illumination:.1f}/100"
    )

    fig5, ax5 = plt.subplots(
        figsize=(10, 6)
    )

    illumination_plot = ax5.imshow(
        illumination_score,
        cmap="plasma"
    )

    ax5.set_title(
        "Lunar Terrain Illumination Proxy"
    )

    ax5.set_xlabel("DEM X")
    ax5.set_ylabel("DEM Y")

    plt.colorbar(
        illumination_plot,
        ax=ax5,
        label="Illumination Proxy"
    )

    st.pyplot(
        fig5,
        clear_figure=True
    )

    st.info(
        "This is a terrain-orientation illumination proxy. "
        "Actual lunar sunlight duration requires solar geometry "
        "or a time-dependent illumination dataset."
    )

    # -------------------------------------------------
    # RESOURCE POTENTIAL
    # -------------------------------------------------

    st.subheader(
        "💧 Lunar Resource Potential"
    )

    st.metric(
        "Terrain-Based Resource Potential",
        f"{average_resource:.1f}/100"
    )

    fig6, ax6 = plt.subplots(
        figsize=(10, 6)
    )

    resource_plot = ax6.imshow(
        resource_potential,
        cmap="cividis"
    )

    ax6.set_title(
        "Lunar Terrain-Based Resource Potential"
    )

    ax6.set_xlabel("DEM X")
    ax6.set_ylabel("DEM Y")

    plt.colorbar(
        resource_plot,
        ax=ax6,
        label="Resource Potential Proxy"
    )

    st.pyplot(
        fig6,
        clear_figure=True
    )

    st.info(
        "This is a terrain-based resource potential proxy "
        "derived from the real lunar DEM. Actual water-ice "
        "and mineral estimates require dedicated scientific datasets."
    )

    # -------------------------------------------------
    # LUNAR SURFACE SCAN - SAFE & HAZARD LOCATIONS
    # -------------------------------------------------

    st.subheader("🌕 Lunar Surface Scan — Safe & Hazard Locations")

    st.caption(
        "Green points show computationally suitable terrain cells. "
        "Red points show potential hazard cells detected from the same real lunar DEM."
    )

    # Select a small number of representative safe points
    # so the map stays clean and attractive.
    visual_safe_mask = (
        np.isfinite(final_score_map)
        & safe_mask
        & (~hazard_mask)
    )

    safe_rows, safe_cols = np.where(visual_safe_mask)
    safe_scores = final_score_map[safe_rows, safe_cols]

    safe_display_n = min(8, len(safe_scores))

    if safe_display_n > 0:
        safe_order = np.argsort(safe_scores)[-safe_display_n:][::-1]
        safe_plot_rows = safe_rows[safe_order]
        safe_plot_cols = safe_cols[safe_order]
    else:
        safe_plot_rows = np.array([], dtype=int)
        safe_plot_cols = np.array([], dtype=int)

    # Select representative high-depression hazard points.
    hazard_rows, hazard_cols = np.where(hazard_mask)
    hazard_values = depression[hazard_rows, hazard_cols]

    hazard_display_n = min(8, len(hazard_values))

    if hazard_display_n > 0:
        hazard_order = np.argsort(hazard_values)[-hazard_display_n:][::-1]
        hazard_plot_rows = hazard_rows[hazard_order]
        hazard_plot_cols = hazard_cols[hazard_order]
    else:
        hazard_plot_rows = np.array([], dtype=int)
        hazard_plot_cols = np.array([], dtype=int)

    fig_scan, ax_scan = plt.subplots(figsize=(11, 7))

    ax_scan.imshow(
        elevation,
        cmap="gray"
    )

    if len(safe_plot_rows) > 0:
        ax_scan.scatter(
            safe_plot_cols,
            safe_plot_rows,
            s=90,
            c="lime",
            edgecolors="white",
            linewidths=1.5,
            label="🟢 Suitable landing point",
            zorder=5
        )

    if len(hazard_plot_rows) > 0:
        ax_scan.scatter(
            hazard_plot_cols,
            hazard_plot_rows,
            s=90,
            c="red",
            edgecolors="white",
            linewidths=1.5,
            label="🔴 Potential hazard point",
            zorder=5
        )

    # Label the strongest few points without overcrowding the map.
    for number, (row, col) in enumerate(
        zip(safe_plot_rows[:3], safe_plot_cols[:3]),
        start=1
    ):
        ax_scan.annotate(
            f"S{number}",
            (col, row),
            xytext=(7, -7),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            color="white"
        )

    for number, (row, col) in enumerate(
        zip(hazard_plot_rows[:3], hazard_plot_cols[:3]),
        start=1
    ):
        ax_scan.annotate(
            f"H{number}",
            (col, row),
            xytext=(7, -7),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold",
            color="white"
        )

    ax_scan.set_title(
        "LUNA-SCAN Real Lunar Surface — Suitable vs Potential Hazard Locations"
    )
    ax_scan.set_xlabel("DEM X")
    ax_scan.set_ylabel("DEM Y")
    ax_scan.legend(loc="upper right")

    st.pyplot(
        fig_scan,
        clear_figure=True
    )

    # Convert displayed points into real latitude/longitude coordinates.
    safe_location_rows = []

    for number, (row, col) in enumerate(
        zip(safe_plot_rows, safe_plot_cols),
        start=1
    ):
        x, y = xy(
            new_transform,
            int(row),
            int(col),
            offset="center"
        )

        try:
            lon, lat = transform(
                original_crs,
                "EPSG:4326",
                [x],
                [y]
            )
            latitude = float(lat[0])
            longitude = float(lon[0])
        except Exception:
            latitude = float(y)
            longitude = float(x)

        safe_location_rows.append({
            "Point": f"S{number}",
            "Status": "🟢 Suitable",
            "Latitude": round(latitude, 6),
            "Longitude": round(longitude, 6),
            "Score": round(float(final_score_map[row, col]), 2),
            "Slope (°)": round(float(slope[row, col]), 2)
        })

    hazard_location_rows = []

    for number, (row, col) in enumerate(
        zip(hazard_plot_rows, hazard_plot_cols),
        start=1
    ):
        x, y = xy(
            new_transform,
            int(row),
            int(col),
            offset="center"
        )

        try:
            lon, lat = transform(
                original_crs,
                "EPSG:4326",
                [x],
                [y]
            )
            latitude = float(lat[0])
            longitude = float(lon[0])
        except Exception:
            latitude = float(y)
            longitude = float(x)

        hazard_location_rows.append({
            "Point": f"H{number}",
            "Status": "🔴 Potential hazard",
            "Latitude": round(latitude, 6),
            "Longitude": round(longitude, 6),
            "Depression": round(float(depression[row, col]), 2),
            "Slope (°)": round(float(slope[row, col]), 2)
        })

    if safe_location_rows:
        st.write("#### 🟢 Suitable Locations")
        st.dataframe(
            pd.DataFrame(safe_location_rows),
            use_container_width=True,
            hide_index=True
        )

    if hazard_location_rows:
        st.write("#### 🔴 Potential Hazard Locations")
        st.dataframe(
            pd.DataFrame(hazard_location_rows),
            use_container_width=True,
            hide_index=True
        )

    st.info(
        "The green and red points are generated from the real lunar DEM used by LUNA-SCAN. "
        "They are computational screening points, not mission-certified landing or hazard locations."
    )

    # -------------------------------------------------
    # FINAL SCORE
    # -------------------------------------------------

    st.subheader(
        "🤖 Final LUNA-SCAN Suitability Analysis"
    )

    st.metric(
        "🌙 Overall LUNA-SCAN Suitability Score",
        f"{overall_score:.1f}/100"
    )

    if overall_score >= 75:
        st.success(
            "🟢 Potentially Suitable Landing Region"
        )
    elif overall_score >= 50:
        st.warning(
            "🟡 Region Needs Further Scientific Analysis"
        )
    else:
        st.error(
            "🔴 Region Has Lower Suitability"
        )

    fig7, ax7 = plt.subplots(
        figsize=(10, 6)
    )

    final_plot = ax7.imshow(
        final_score_map,
        cmap="viridis"
    )

    ax7.set_title(
        "LUNA-SCAN Overall Suitability Map"
    )

    ax7.set_xlabel("DEM X")
    ax7.set_ylabel("DEM Y")

    plt.colorbar(
        final_plot,
        ax=ax7,
        label="Suitability Score"
    )

    st.pyplot(
        fig7,
        clear_figure=True
    )

    # -------------------------------------------------
    # TOP CANDIDATE SITES
    # -------------------------------------------------

    st.subheader(
        "📍 Top Candidate Landing Sites"
    )

    if not candidate_table.empty:

        st.dataframe(
            candidate_table,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            "🛰️ Top candidate locations were automatically "
            "selected from the highest-scoring DEM cells."
        )

    else:

        st.warning(
            "No computational candidate locations were found."
        )

    # -------------------------------------------------
    # EXPLAINABLE RESULT
    # -------------------------------------------------

    st.subheader(
        "🔍 Explainable LUNA-SCAN Result"
    )

    if not candidate_table.empty:

        best_site = candidate_table.iloc[0]

        best_lat = best_site["Latitude"]
        best_lon = best_site["Longitude"]
        best_score = best_site["Suitability Score"]
        best_slope = best_site["Slope (°)"]

        st.success(
            f"🟢 Best Computational Candidate: "
            f"Latitude {best_lat}, Longitude {best_lon}"
        )

        e1, e2, e3 = st.columns(3)

        e1.metric(
            "🤖 Suitability",
            f"{best_score}/100"
        )

        e2.metric(
            "⛰️ Local Slope",
            f"{best_slope}°"
        )

        e3.metric(
            "⚠️ Hazard Cells",
            f"{hazard_count:,}"
        )

        st.write("### Why this location was selected")

        if best_slope < avg_slope:
            st.write(
                "✅ The candidate has a relatively lower "
                "local slope than the analysed region."
            )
        else:
            st.write(
                "⚠️ The candidate has a relatively higher "
                "local slope and needs further analysis."
            )

        st.write(
            f"☀️ Regional illumination proxy: "
            f"{average_illumination:.1f}/100"
        )

        st.write(
            f"💧 Terrain-based resource potential: "
            f"{average_resource:.1f}/100"
        )

        st.write(
            f"🛰️ Overall regional suitability score: "
            f"{overall_score:.1f}/100"
        )

    # -------------------------------------------------
    # SCIENTIFIC STATUS
    # -------------------------------------------------

    st.subheader(
        "🔬 Scientific Data Status"
    )

    st.success(
        "✅ Real lunar DEM successfully analysed."
    )

    st.info(
        "⛰️ Elevation and slope are derived directly "
        "from the lunar DEM."
    )

    st.warning(
        "⚠️ Hazard, illumination and resource sections "
        "currently use computational proxy methods. "
        "Dedicated scientific datasets are required before "
        "these can be treated as direct measurements."
    )

    st.caption(
        "LUNA-SCAN is a hackathon/research prototype. "
        "Its scores are computational screening results and "
        "are not mission-certified landing recommendations."
    )

except FileNotFoundError:

    st.error(
        f"❌ DEM file not found: {dem_file}"
    )

except Exception as e:

    st.error(
        f"❌ Analysis error: {e}"
    )

