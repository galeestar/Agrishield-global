import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="AgriShield | Global Crop & Soil Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- CACHED SATELLITE AGRO-WEATHER ENGINE (100% FREE, NO API KEY) ---
@st.cache_data(ttl=1800)
def fetch_agro_telemetry(lat: float, lon: float):
    url = (
        "https://open-meteo.com"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration"
        "&hourly=soil_moisture_0_to_1cm,soil_moisture_3_to_9cm"
        "&timezone=auto"
    )
    try:
        res = requests.get(url, timeout=12)
        res.raise_for_status()
        return res.json()
    except Exception:
        return {}


# --- SIDEBAR: FARM REGION & CROP PROFILE ---
with st.sidebar:
    st.title("🌾 AgriShield Global")
    st.caption("Open-Source Soil, Irrigation & Food Security Planner")

    agricultural_zones = {
        "Central Valley, California, USA": (36.7783, -119.4179),
        "Pampas Breadbasket, Argentina": (-34.6037, -58.3816),
        "Punjab Agricultural Belt, India": (30.9010, 75.8573),
        "Rift Valley Farmlands, Kenya": (-0.3031, 36.0800),
        "Loire Valley, France": (47.3941, 0.6848),
        "Mekong Delta, Vietnam": (10.0452, 105.7469),
        "Custom Coordinates...": (0.0, 0.0),
    }

    zone_choice = st.selectbox("Select Agricultural Region", list(agricultural_zones.keys()), index=0)
    if zone_choice == "Custom Coordinates...":
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=6.5244, format="%.4f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=3.3792, format="%.4f")
    else:
        lat, lon = agricultural_zones[zone_choice]

    st.divider()
    st.markdown(
        """
        **🌍 Why This Matters:**
        * Prevents groundwater waste via **FAO Evapotranspiration (ET₀)** math
        * Protects smallholders against sudden heatwaves & dry spells
        * Promotes soil-restoring crop rotations
        """
    )

    if st.button("🔄 Sync Satellite Soil Feed", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- MAIN HEADER ---
st.title("🌾 AgriShield: Global Crop Resilience & Irrigation Hub")
st.caption("Satellite soil moisture tracking, precision irrigation calculator & sustainable crop rotation planner")

tab_soil, tab_water, tab_rotation = st.tabs(
    [
        "🛰️ Soil Moisture & Evapotranspiration",
        "💧 Precision Irrigation Calculator",
        "🔄 Sustainable Crop Rotation Planner",
    ]
)

# ==============================================================================
# TAB 1: SATELLITE SOIL MOISTURE & EVAPOTRANSPIRATION (OPEN-METEO)
# ==============================================================================
with tab_soil:
    st.subheader(f"🛰️ 7-Day Agro-Weather & Soil Telemetry ({lat:.2f}°, {lon:.2f}°)")
    agro = fetch_agro_telemetry(lat, lon)

    if agro and "daily" in agro:
        daily = agro["daily"]
        hourly = agro.get("hourly", {})

        df_daily = pd.DataFrame(
            {
                "Date": daily["time"],
                "Max Temp (°C)": daily["temperature_2m_max"],
                "Min Temp (°C)": daily["temperature_2m_min"],
                "Rainfall (mm)": daily["precipitation_sum"],
                "Water Loss ET₀ (mm)": daily["et0_fao_evapotranspiration"],
            }
        )
        df_daily["Net Water Balance (mm)"] = (
            df_daily["Rainfall (mm)"] - df_daily["Water Loss ET₀ (mm)"]
        ).round(2)

        total_rain = float(df_daily["Rainfall (mm)"].sum())
        total_et0 = float(df_daily["Water Loss ET₀ (mm)"].sum())
        net_balance = total_rain - total_et0

        soil_now = 0.25
        if hourly and "soil_moisture_3_to_9cm" in hourly and hourly["soil_moisture_3_to_9cm"]:
            soil_now = float(hourly["soil_moisture_3_to_9cm"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Root-Zone Moisture", f"{soil_now * 100:.1f}%")
        m2.metric("7-Day Expected Rain", f"{total_rain:.1f} mm")
        m3.metric("7-Day Evaporation Loss", f"{total_et0:.1f} mm")
        m4.metric(
            "Net Soil Water Balance",
            f"{net_balance:+.1f} mm",
            "Surplus" if net_balance >= 0 else "Irrigation Needed",
        )

        fig_water = px.bar(
            df_daily,
            x="Date",
            y=["Rainfall (mm)", "Water Loss ET₀ (mm)"],
            barmode="group",
            template="plotly_dark",
            title="Daily Rainfall vs. Crop Evapotranspiration Water Loss",
        )
        fig_water.update_layout(height=380)
        st.plotly_chart(fig_water, use_container_width=True)

        st.dataframe(df_daily, use_container_width=True, hide_index=True)
    else:
        st.warning("Satellite telemetry temporarily unavailable for these coordinates.")

# ==============================================================================
# TAB 2: PRECISION IRRIGATION & WATER CONSERVATION CALCULATOR
# ==============================================================================
with tab_water:
    st.subheader("💧 Precision Crop Water Requirement Calculator")
    st.caption("Calculate exact water volumes to prevent crop stress and eliminate water waste.")

    crop_kc = {
        "Maize / Corn (Kc = 1.15)": (1.15, 4.5),
        "Rice (Kc = 1.20)": (1.20, 6.0),
        "Wheat / Barley (Kc = 1.05)": (1.05, 3.8),
        "Tomatoes & Vegetables (Kc = 1.10)": (1.10, 4.2),
        "Soybeans / Legumes (Kc = 0.95)": (0.95, 3.5),
        "Cassava / Root Crops (Kc = 0.85)": (0.85, 3.0),
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        selected_crop = st.selectbox("Select Crop Type", list(crop_kc.keys()))
        kc_factor, avg_yield_tons = crop_kc[selected_crop]
    with c2:
        field_hectares = st.number_input("Field Area (Hectares)", min_value=0.1, value=2.0, step=0.5)
    with c3:
        irrigation_eff = st.selectbox(
            "Irrigation Method",
            [
                "Drip Irrigation (90% Efficient)",
                "Sprinkler System (75% Efficient)",
                "Surface / Furrow Flooding (60% Efficient)",
            ],
        )

    eff_map = {
        "Drip Irrigation (90% Efficient)": 0.90,
        "Sprinkler System (75% Efficient)": 0.75,
        "Surface / Furrow Flooding (60% Efficient)": 0.60,
    }
    efficiency = eff_map[irrigation_eff]

    # Use live ET0 if available, otherwise fallback to 4.5 mm/day
    daily_et0 = 4.5
    if agro and "daily" in agro and agro["daily"].get("et0_fao_evapotranspiration"):
        daily_et0 = float(pd.Series(agro["daily"]["et0_fao_evapotranspiration"]).mean())

    crop_water_mm = daily_et0 * kc_factor
    # 1 mm of water over 1 hectare (10,000 m²) = 10,000 liters
    gross_liters_day = (crop_water_mm * 10000 * field_hectares) / efficiency
    drip_liters_day = (crop_water_mm * 10000 * field_hectares) / 0.90
    water_saved_drip = max(0.0, gross_liters_day - drip_liters_day)

    w1, w2, w3 = st.columns(3)
    w1.metric("Daily Crop Need", f"{crop_water_mm:.2f} mm / day")
    w2.metric("Total Water Required", f"{gross_liters_day:,.0f} Liters / day")
    w3.metric("Potential Drip Savings", f"{water_saved_drip:,.0f} Liters / day")

# ==============================================================================
# TAB 3: SUSTAINABLE CROP ROTATION & HARVEST PLANNER
# ==============================================================================
with tab_rotation:
    st.subheader("🔄 Soil-Restoring 4-Season Crop Rotation Planner")
    st.caption(
        "Rotating crop families naturally replenishes soil nitrogen, breaks pest cycles, and boosts long-term yields."
    )

    rotation_plans = pd.DataFrame(
        [
            {
                "Season": "Season 1 (Heavy Feeder)",
                "Recommended Crop": "Maize / Sweet Corn or Wheat",
                "Soil Impact": "Consumes high nitrogen; builds organic biomass",
                "Est. Harvest Window": "90 – 120 Days",
            },
            {
                "Season": "Season 2 (Nitrogen Fixer)",
                "Recommended Crop": "Soybeans, Cowpeas, or Lentils",
                "Soil Impact": "Symbiotic root bacteria fix atmospheric nitrogen back into soil",
                "Est. Harvest Window": "75 – 100 Days",
            },
            {
                "Season": "Season 3 (Deep Root / Leafy)",
                "Recommended Crop": "Tomatoes, Cabbage, or Sunflower",
                "Soil Impact": "Breaks up compacted subsoil and utilizes residual nutrients",
                "Est. Harvest Window": "65 – 90 Days",
            },
            {
                "Season": "Season 4 (Root & Cover Rest)",
                "Recommended Crop": "Sweet Potatoes, Carrots, or Clover Cover",
                "Soil Impact": "Prevents soil erosion, suppresses weeds, and restores moisture retention",
                "Est. Harvest Window": "80 – 110 Days",
            },
        ]
    )

    st.dataframe(rotation_plans, use_container_width=True, hide_index=True)

    est_total_harvest = avg_yield_tons * field_hectares
    st.success(
        f"🌱 **Estimated Harvest Output:** Planting **{selected_crop.split(' (')}** across **{field_hectares} hectares** yields approximately **{est_total_harvest:.1f} metric tons** of food per cycle."
    )

st.divider()
st.caption("AgriShield Open Telemetry • Satellite weather & evapotranspiration via Open-Meteo FAO-56")
