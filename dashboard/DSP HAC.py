import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from scipy.signal import butter, filtfilt

WEB_URL = "https://script.google.com/macros/s/AKfycby_Sw6tnYdCYdDiIqwUxEnf9q3Et6by_RvtA__dsZe86vySC27a7UzrjK6DCXGLZESR/exec"

st.set_page_config(page_title="Stress Dashboard", layout="centered")

# --------------------- FETCH DATA --------------------- #
def fetch_data():
    try:
        r = requests.get(WEB_URL, params={"_": time.time()}, timeout=5)
        data = r.json()
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index("time")
        df[["gsr","hr","temp"]] = df[["gsr","hr","temp"]].apply(pd.to_numeric, errors="coerce")
        return df.ffill().bfill()
    except:
        return pd.DataFrame()


# --------------------- FILTERS --------------------- #
def butter_lowpass(x, cutoff=0.7, fs=4, order=4):
    ny = fs / 2
    b,a = butter(order, cutoff/ny, btype="low")
    try: return filtfilt(b,a,x)
    except: return x

def butter_bandpass(x, low=0.05, high=1.5, fs=4, order=4):
    ny = fs / 2
    b,a = butter(order, [low/ny, high/ny], btype="band")
    try: return filtfilt(b,a,x)
    except: return x

def normalize(x):
    if np.max(x) == np.min(x):
        return np.zeros_like(x)
    return (x - np.min(x)) / (np.max(x) - np.min(x))


# --------------------- TIPS --------------------- #
def get_tip(level):
    if level == "LOW":
        return "Your day seems to be going well 😊"
    elif level == "MODERATE":
        return "Calm down… you got this 💛"
    else:
        return "Take deep breaths… you can handle this ❤️‍🔥"


# --------------------- UI START --------------------- #
st.title("🧠 Real-Time Stress Monitor")
st.write("Updated every **3 seconds**")

placeholder = st.empty()

while True:
    df = fetch_data()

    if df.empty:
        st.warning("Waiting for ESP32 data...")
        time.sleep(3)
        continue

    # Resample to 4 Hz
    df_rs = df.resample("250ms").mean().interpolate()

    # Filters
    df_rs["gsr_f"] = butter_bandpass(df_rs["gsr"].values)
    df_rs["hr_f"]  = butter_lowpass(df_rs["hr"].values)
    df_rs["temp_f"] = df_rs["temp"].values  # raw

    # Normalized values
    gsr_n = normalize(df_rs["gsr_f"])[-1]
    hr_n  = normalize(df_rs["hr_f"])[-1]
    temp_n = normalize(df_rs["temp_f"])[-1]

    # Stress score
    stress = round(0.4*gsr_n + 0.4*hr_n + 0.2*temp_n, 3)

    # Determine level + emoji
    if stress < 0.33:
        level = "LOW"
        color = "#00cc44"
        emoji = "😊"
        pulse = False
    elif stress < 0.66:
        level = "MODERATE"
        color = "#ffcc00"
        emoji = "😐"
        pulse = False
    else:
        level = "HIGH"
        color = "#ff3333"
        emoji = "😟"
        pulse = True

    tip = get_tip(level)

    # ---------------- DISPLAY ---------------- #
    with placeholder.container():

        # Stress Score Bubble
        st.markdown(f"""
            <div style="
                padding:20px;
                background:{color};
                color:white;
                border-radius:20px;
                text-align:center;
                width:60%;
                margin:auto;
                font-size:40px;
                {'animation: pulse 1.2s infinite;' if pulse else ''}
            ">
                {stress}
            </div>

            <style>
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.08); }}
                100% {{ transform: scale(1); }}
            }}
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"## **{emoji} Stress Level: {level}**")
        st.markdown(f"### 💡 *{tip}*")

        st.markdown("---")

        # Show raw sensor values only
        st.subheader("📊 Latest Sensor Readings")
        clean_df = df.tail(5)[["gsr", "hr", "temp"]]
        st.dataframe(clean_df)

    time.sleep(3)
