import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- Setup ---
API_KEY = st.secrets["GOVEE_API_KEY"]
BASE_URL = "https://openapi.api.govee.com/router/api/v1"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

st.set_page_config(layout="wide")
st.title("🌡️ Govee Live Temperature Dashboard")

# --- Load Devices ---
@st.cache_data(ttl=3600)
def get_thermometers():
    url = f"{BASE_URL}/user/devices"
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    all_devices = res.json()["data"]
    return [
        d for d in all_devices
        if any(cap.get("instance") == "temperature" for cap in d.get("capabilities", []))
    ]

devices = get_thermometers()

# Add this after fetching devices
st.subheader("🔍 Raw Device JSON")
st.json(devices)  # Shows the full API response

def is_thermometer(device):
    for cap in device.get("capabilities", []):
        # Check if capability instance or unit mentions temperature
        if (
            "temperature" in cap.get("instance", "").lower() or
            "temperature" in str(cap.get("parameters", {}).get("unit", "")).lower()
        ):
            return True
    return False

thermometers = [d for d in devices if is_thermometer(d)]


if not devices:
    st.error("No thermometer devices found in your account.")
else:
    device_options = {
        f"{d.get('deviceName', d['device'])} ({d['device']})": d["device"]
        for d in devices
    }
    selected_label = st.selectbox("Select a Thermometer", list(device_options.keys()))
    selected_device = device_options[selected_label]

    # --- Placeholder for live data fetch (replace with correct endpoint when known) ---
    st.subheader("Current Temperature (Placeholder)")
    demo_temp = round(22 + (datetime.now().second % 10) * 0.1, 1)
    st.metric("Temperature", f"{demo_temp} °C")

    # --- Simulated history chart ---
    st.subheader("📈 Temperature Trend (Simulated Data)")
    history = pd.DataFrame({
        "timestamp": pd.date_range(end=datetime.now(), periods=24, freq="H"),
        "temperature": [round(22 + i % 5 * 0.3, 1) for i in range(24)]
    })
    fig = px.line(history, x="timestamp", y="temperature", title="24h Temperature History")
    st.plotly_chart(fig, use_container_width=True)
