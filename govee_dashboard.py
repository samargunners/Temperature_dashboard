import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time
import uuid

# --- CONFIG ---
API_KEY = "f773607f-9d19-4b7d-b532-b291f1d1026b"
BASE_URL = "https://openapi.api.govee.com/router/api/v1"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}

ALERT_TEMP_THRESHOLD = 5.0  # degrees Celsius

# --- STEP 1: Get All Devices ---
def get_all_devices():
    url = f"{BASE_URL}/user/devices"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]

# --- STEP 2: Filter Thermometers ---
def extract_thermometers(device_list):
    rows = []
    for device in device_list:
        capabilities = [cap["instance"] for cap in device.get("capabilities", [])]
        if "sensorTemperature" in capabilities:
            rows.append({
                "Device Name": device.get("deviceName", device["device"]),
                "Device ID": device["device"],
                "SKU": device["sku"]
            })
    return pd.DataFrame(rows)

# --- STEP 3: Get Real-Time Readings ---
def get_device_state(device_id, sku):
    url = f"{BASE_URL}/device/state"
    payload = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "device": device_id,
            "sku": sku
        }
    }
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        data = response.json().get("data", {})
        temp = humidity = None
        for prop in data.get("properties", []):
            if prop["instance"] == "sensorTemperature":
                temp = prop["value"]
            elif prop["instance"] == "sensorHumidity":
                humidity = prop["value"]
        return temp, humidity
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e} → {response.text}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

# --- STEP 4: Compile Dashboard Table ---
def build_dashboard_df(devices_df):
    rows = []
    for _, row in devices_df.iterrows():
        temp, humidity = get_device_state(row["Device ID"], row["SKU"])
        rows.append({
            "Device Name": row["Device Name"],
            "Temperature (°C)": temp,
            "Humidity (%)": humidity,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        time.sleep(1)  # Respect API limits
    return pd.DataFrame(rows)

# --- STEP 5: Run Everything ---
all_devices = get_all_devices()
thermo_df = extract_thermometers(all_devices)
dashboard_df = build_dashboard_df(thermo_df)

# --- STEP 6: Display Alerting Table ---
alerts_df = dashboard_df[dashboard_df["Temperature (°C)"] > ALERT_TEMP_THRESHOLD]

if not alerts_df.empty:
    print("⚠️ ALERT: Devices exceeding threshold:")
    print(alerts_df)
else:
    print("✅ All devices are within safe temperature range.")

# --- STEP 7: Plot Temperature Bar Chart with Alert Highlight ---
dashboard_df_sorted = dashboard_df.sort_values("Temperature (°C)")

# Color logic: red for alert, green for safe
colors = [
    "gray" if temp is None else ("red" if temp > ALERT_TEMP_THRESHOLD else "green")
    for temp in dashboard_df_sorted["Temperature (°C)"]
]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(dashboard_df_sorted["Device Name"], dashboard_df_sorted["Temperature (°C)"], color=colors)
ax.set_title("🌡️ Temperature by Device with Alerts")
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Device")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
