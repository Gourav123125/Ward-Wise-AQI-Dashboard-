def calculate_score(pm25, pm10, no2):
    return 0.5 * pm25 + 0.3 * pm10 + 0.2 * no2

def classify_pollution(aqi):
    aqi = int(float(aqi))
    if aqi <= 50:
        return "Good", "🟢"
    elif aqi <= 100:
        return "Satisfactory", "🟢"
    elif aqi <= 200:
        return "Moderate", "🟡"
    elif aqi <= 300:
        return "Poor", "🟠"
    elif aqi <= 400:
        return "Very Poor", "🔴"
    else:
        return "Severe", "🔴"


def aqi_color(aqi: int) -> str:
    aqi = int(float(aqi))
    if aqi <= 50:
        return "#00e400"      # Good
    elif aqi <= 100:
        return "#9cff57"      # Satisfactory
    elif aqi <= 200:
        return "#f2c94c"      # Moderate
    elif aqi <= 300:
        return "#f2994a"      # Poor
    elif aqi <= 400:
        return "#d5433e"      # Very Poor
    else:
        return "#7e0023"      # Severe





def recommend_actions(ward_aqi, traffic, construction, industry):
    actions = []

    if ward_aqi >= 300 and traffic == "High":
        actions.append(("Restrict Heavy Vehicles", "Delhi Traffic Police"))

    if construction == "Yes" and ward_aqi >= 200:
        actions.append(("Increase Water Sprinkling", "MCD"))

    if ward_aqi >= 400 and construction == "Yes":
        actions.append(("Halt Construction Activities", "DPCC"))

    return actions

def simulate_ward_aqi(city_aqi, traffic, construction, industry, ward_name=None):
    adjustment = 0

    if traffic == "High":
        adjustment += 40
    elif traffic == "Medium":
        adjustment += 25
    else:
        adjustment += 10

    if construction == "Yes":
        adjustment += 30

    if industry == "Yes":
        adjustment += 45

    ward_aqi = city_aqi + adjustment

    # 🔥 Force demo hotspots
    if ward_name in HIGH_RISK_WARDS:
        ward_aqi = max(ward_aqi, HIGH_RISK_WARDS[ward_name])

    # Baseline floor
    if ward_aqi < 80:
        ward_aqi = 80

    return int(ward_aqi)



def simulate_pm25(pm25, reduction):
    return round(pm25 * (1 - reduction / 100), 1)
HIGH_RISK_WARDS = {
    "Karol Bagh": 180,
    "Chandni Chowk": 220,
    "Okhla": 260
}

