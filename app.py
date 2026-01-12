import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from utils import *
import os



st.set_page_config(
    page_title="Delhi Ward Pollution Action Recommender",
    layout="wide",
    page_icon="🌫️"
)

API_TOKEN = "fc3fb4c8a94b2d79161bf05afc7915ad5a0a3473"




DEFAULT_HEADER_BG_URL = "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1600&q=60"

try:
    header_bg_url = st.secrets["HEADER_BG_URL"]
except Exception:
    header_bg_url = os.getenv("HEADER_BG_URL", DEFAULT_HEADER_BG_URL)



st.sidebar.title("Ward Lookup")



def aqi_bar_color(aqi: int) -> str:
    aqi = int(float(aqi))
    # WAQI colors [web:181]
    if aqi <= 50:
        return "#00e400"
    if aqi <= 100:
        return "#ffff00"
    if aqi <= 150:
        return "#ff7e00"
    if aqi <= 200:
        return "#ff0000"
    if aqi <= 300:
        return "#8f3f97"
    return "#7e0023"



def aqi_bar_gradient(aqi: int) -> str:
    c = aqi_bar_color(aqi)
    # subtle gradient using same base color
    return f"linear-gradient(90deg, {c}, {c}CC)"


def action_ui(act: str):
    a = act.lower()
    if "restrict" in a:
        return ("🚚", "#d5433e", "🚗")
    if "sprinkling" in a or "water" in a:
        return ("💧", "#53a151", "🚿")
    if "halt" in a or "construction" in a:
        return ("⚠️", "#e5b364", "🧱")
    return ("📌", "#0e417f", "➜")


st.markdown(f"""
<style>
iframe {{
  width: 100% !important;
}}

.stApp {{
    background: #E3E9FF;
}}

.block-container {{
    padding-top: 0.8rem;
    padding-bottom: 1.0rem;
    max-width: 100% !important;
    padding-left: clamp(12px, 2vw, 28px);
    padding-right: clamp(12px, 2vw, 28px);
}}

@media (min-width: 1800px) {{
  .block-container {{
    max-width: 1650px !important;
    margin: 0 auto;
  }}
}}

[data-testid="stSidebar"] {{
    background: #e7edf6 !important;
    border-right: 2px solid rgba(11,46,89,0.12);
}}
[data-testid="stSidebar"] > div {{
    background: #E3E9FF !important;
}}

.poster {{
    background: #f3f6fb;
    border: 2px solid rgba(11,46,89,0.18);
    border-radius: 14px;
    box-shadow: 0px 14px 30px rgba(0,0,0,0.12);
    padding: 12px;
}}

.header-box {{
    background:
      linear-gradient(180deg, rgba(11,46,89,0.82), rgba(14,65,127,0.88)),
      url('{header_bg_url}');
    background-size: cover;
    background-position: center;
    padding: 18px 18px 14px 18px;
    border-radius: 12px;
    color: white;
    margin-bottom: 12px;

    border: 2px solid rgba(255,255,255,0.14);
    box-shadow: 0px 12px 28px rgba(0,0,0,0.16);
    text-align: center;
}}

.header-title {{
    font-size: clamp(20px, 1.3vw + 14px, 28px);
    font-weight: 800;
    letter-spacing: 0.2px;
    line-height: 1.15;
}}
.header-sub {{
    font-size: clamp(11px, 0.5vw + 9px, 14px);
    opacity: 0.92;
    font-weight: 600;
    margin-top: 4px;
}}
.header-chip {{
    background: rgba(245,248,255,0.95);
    color: #0b2e59;
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 11px;
    margin-top: 10px;
    font-weight: 800;
    border: 1.6px solid rgba(11,46,89,0.18);
    box-shadow: 0px 8px 16px rgba(0,0,0,0.10);
}}

.card {{
    background: #ffffff;
    border-radius: 12px;
    padding: 12px;

    border: 2px solid rgba(11,46,89,0.20);
    box-shadow: 0px 10px 22px rgba(0,0,0,0.10);

    margin-bottom: 12px;
    position: relative;
}}
.card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    background: linear-gradient(90deg, rgba(11,46,89,0.32), rgba(11,46,89,0.06));
}}

.map-frame {{
    border: 2px solid rgba(11,46,89,0.14);
    border-radius: 10px;
    overflow: hidden;
    background: #eef3fb;
}}

/* AQI bar gets its actual color inline from Python */
.aqi-box {{
    color: white;
    padding: 10px 12px;
    border-radius: 10px;
    font-weight: 900;
    font-size: 14px;

    border: 1.6px solid rgba(255,255,255,0.20);
    box-shadow: 0px 10px 18px rgba(0,0,0,0.14);
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.info-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 0;
    font-size: 12px;
    color: #0b2e59;
    border-top: 1px solid rgba(207,216,230,0.85);
}}
.info-row:first-of-type {{
    border-top: none;
    padding-top: 8px;
}}
.bullet {{
    width: 18px;
    height: 18px;
    border-radius: 6px;
    background: #eef4ff;
    border: 1.4px solid rgba(11,46,89,0.16);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
}}

.action-item {{
    display: grid;
    grid-template-columns: 34px 1fr 44px;
    gap: 10px;
    background: #f3f6fb;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 10px;
    align-items: center;

    border: 1.8px solid rgba(11,46,89,0.14);
    box-shadow: 0px 8px 16px rgba(0,0,0,0.06);
}}
.action-icon {{
    width: 34px;
    height: 34px;
    border-radius: 12px;
    display:flex;
    align-items:center;
    justify-content:center;
    color: #fff;
    font-weight: 900;
    border: 1px solid rgba(255,255,255,0.20);
}}
.action-right {{
    width: 44px;
    height: 30px;
    border-radius: 10px;
    background: #ffffff;
    border: 1.4px solid rgba(11,46,89,0.14);
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight: 900;
    color: #0b2e59;
}}
.action-text b {{
    color: #0b2e59;
}}
.action-text small {{
    color: #6b7a90;
    font-weight: 700;
}}

.whatif {{
    background: #f8fafc;
    border-radius: 12px;
    padding: 10px;
    margin-top: 10px;

    border: 1.8px solid rgba(11,46,89,0.14);
    box-shadow: 0px 8px 16px rgba(0,0,0,0.06);
}}
.kv {{
    display:flex;
    justify-content: space-between;
    align-items:center;
    font-size: 12px;
    color: #22324a;
    padding: 6px 0;
    border-bottom: 1px solid rgba(207,216,230,0.85);
}}
.kv:last-child {{
    border-bottom: none;
}}
.dot {{
    width: 10px;
    height: 10px;
    border-radius: 999px;
    display:inline-block;
    margin-left: 6px;
    border: 1px solid rgba(0,0,0,0.18);
}}

h3 {{
    margin-top: 6px !important;
    margin-bottom: 10px !important;
}}

@media (max-width: 1100px) {{
  .poster {{ padding: 10px; }}
}}
</style>
""", unsafe_allow_html=True)



st.markdown('<div class="poster">', unsafe_allow_html=True)

st.markdown(f"""
<div class="header-box">
    <div class="header-title">Delhi Ward Pollution Action Recommender</div>
    <div class="header-sub">Actionable Air Quality Interventions for Municipal Governance</div>
    <div class="header-chip">Designed for Delhi Municipal Corporations & DPCC</div>
</div>
""", unsafe_allow_html=True)



df = pd.read_csv("data/ward_data.csv")



ward = st.sidebar.selectbox("Select Ward", df["ward"])
ward_info = df[df["ward"] == ward].iloc[0]



@st.cache_data(ttl=600)
def fetch_aqi():
    url = f"https://api.waqi.info/feed/delhi/?token={API_TOKEN}"
    res = requests.get(url).json()
    if res["status"] == "ok":
        iaqi = res["data"]["iaqi"]
        return (
            iaqi.get("pm25", {}).get("v", 0),
            iaqi.get("pm10", {}).get("v", 0),
            iaqi.get("no2", {}).get("v", 0),
            res["data"]["aqi"],
            res["data"]["time"]["s"]
        )
    return 0, 0, 0, 0, "N/A"


pm25, pm10, no2, city_aqi, timestamp = fetch_aqi()


ward_aqi = simulate_ward_aqi(
    city_aqi,
    ward_info.get("traffic", "Low"),
    ward_info.get("construction", "No"),
    ward_info.get("industry", "No"),
    ward_name
)

level, icon = classify_pollution(ward_aqi)
actions = recommend_actions(
    ward_aqi,
    ward_info.traffic,
    ward_info.construction,
    ward_info.industry
)


left, right = st.columns([1.2, 1], gap="medium")


with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### Ward AQI Levels")

    st.markdown('<div class="map-frame">', unsafe_allow_html=True)

    m = folium.Map(
        location=[28.6139, 77.2090],
        zoom_start=11,
        tiles="cartodbpositron"
    )

    for _, row in df.iterrows():
        w_aqi = simulate_ward_aqi(
            city_aqi,
            row.traffic,
            row.construction,
            row.industry
        )

        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=9,
            popup=f"<b>{row.ward}</b><br>AQI: {w_aqi}",
            color=aqi_color(w_aqi),
            fill=True,
            fill_color=aqi_color(w_aqi),
            fill_opacity=0.85
        ).add_to(m)

    st_folium(m, height=360, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1], gap="small")
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Ward AQI Levels**")
        st.markdown("""
        <div style="margin-top:6px; font-size:12px; color:#0b2e59;">
          <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid rgba(207,216,230,0.85);">
            <span style="width:12px;height:12px;border-radius:3px;background:#53a151;border:1px solid rgba(0,0,0,0.18);display:inline-block;"></span> Good
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid rgba(207,216,230,0.85);">
            <span style="width:12px;height:12px;border-radius:3px;background:#f2c94c;border:1px solid rgba(0,0,0,0.18);display:inline-block;"></span> Moderate
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid rgba(207,216,230,0.85);">
            <span style="width:12px;height:12px;border-radius:3px;background:#f2994a;border:1px solid rgba(0,0,0,0.18);display:inline-block;"></span> Poor
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid rgba(207,216,230,0.85);">
            <span style="width:12px;height:12px;border-radius:3px;background:#d5433e;border:1px solid rgba(0,0,0,0.18);display:inline-block;"></span> Very Poor
          </div>
          <div style="display:flex;align-items:center;gap:10px;padding:6px 0;">
            <span style="width:12px;height:12px;border-radius:3px;background:#b91c1c;border:1px solid rgba(0,0,0,0.18);display:inline-block;"></span> Severe
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="map-frame">', unsafe_allow_html=True)
        st_folium(m, height=190, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # ---------------- Ward Overview ----------------
    st.markdown(f"### {ward} Ward Overview")

    # AQI bar
    bar_color = aqi_color(ward_aqi)
    st.markdown(
        f"""
        <div class="aqiBar" style="background:{bar_color};">
            <div>AQI: {ward_aqi} • {level} ❗ </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="info-row"><span class="bullet">▶</span>
            <div><b>Level:</b> {level}</div>
        </div>
        <div class="info-row"><span class="bullet">▶</span>
            <div><b>Primary Source:</b> Vehicular Emissions</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    st.markdown("### Recommended Actions")

    fallback_actions = [
        ("Restrict Heavy Vehicles", "Delhi Traffic Police"),
        ("Increase Water Sprinkling", "MCD"),
        ("Halt Construction Activities", "DPCC"),
    ]

    normalized_actions = list(actions)[:3]
    if len(normalized_actions) < 3:
        for item in fallback_actions:
            if len(normalized_actions) >= 3:
                break
            if item not in normalized_actions:
                normalized_actions.append(item)

   
    idx = sum(ord(c) for c in ward) % len(normalized_actions)

    act, auth = normalized_actions[idx]
    left_emoji, color, right_emoji = action_ui(act)

    st.markdown(
        f"""
        <div class="action-item">
            <div class="action-icon" style="background:{color};">{left_emoji}</div>
            <div class="action-text">
                <b>{act}</b><br>
                <small>{auth}</small>
            </div>
            <div class="action-right">{right_emoji}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    st.markdown("### Action Impact Simulation")

    impact_label = ""
    impact_factor = 0

    if "Heavy Vehicles" in act:
        impact_label = "Traffic Reduction (%)"
        impact_factor = 0.6
    elif "Water Sprinkling" in act:
        impact_label = "Dust Suppression (%)"
        impact_factor = 0.4
    elif "Halt Construction" in act:
        impact_label = "Construction Halt (%)"
        impact_factor = 0.7
    elif "Industrial" in act:
        impact_label = "Industrial Compliance (%)"
        impact_factor = 0.8

    impact_value = st.slider(
        impact_label,
        0, 50, 30,
        key=f"impact_{ward}"
    )

    reduction_amount = int(ward_aqi * (impact_value / 100) * impact_factor)
    new_aqi = max(ward_aqi - reduction_amount, 0)

    new_level, _ = classify_pollution(new_aqi)
    new_color = aqi_color(new_aqi)

    st.markdown(
        f"""
        <div class="whatif">
            <div class="kv"><span><b>Action:</b></span><span>{act}</span></div>
            <div class="kv"><span><b>Impact Applied:</b></span><span>{impact_value}%</span></div>
            <div class="kv"><span><b>Estimated AQI:</b></span><span>{new_aqi}</span></div>
            <div class="kv">
                <span><b>New AQI Level:</b></span>
                <span>{new_level}
                    <span class="dot" style="background:{new_color};"></span>
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

   
    st.markdown('</div>', unsafe_allow_html=True)


st.caption("Prototype Dashboard • WAQI Data • Policy Decision Support System")

st.markdown('</div>', unsafe_allow_html=True)
