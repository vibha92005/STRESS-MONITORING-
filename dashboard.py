import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from scipy.signal import butter, filtfilt
from scipy.fft import rfft, rfftfreq

WEB_URL = "https://script.google.com/macros/s/AKfycbyn55IlgA1tKG5nLikQZWbDc3ih-tTTfIAa_rFcG3u-w9qntoFGlWJpydJDzHXjkv8I/exec"

st.set_page_config(page_title="Simple Stress Dashboard", layout="centered")

# -------------------------- HELPERS -------------------------- #

def fetch_data():
    """Fetch Google Sheet data using Apps Script URL"""
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

def butter_filt_lowpass(x, cutoff=0.7, fs=4, order=4):
    try:
        ny = fs / 2
        b, a = butter(order, cutoff/ny, btype="low")
        return filtfilt(b, a, x)
    except:
        return x   # fallback if filtering fails

def butter_filt_bandpass(x, low=0.05, high=1.5, fs=4, order=4):
    try:
        ny = fs / 2
        b, a = butter(order, [low/ny, high/ny], btype="band")
        return filtfilt(b, a, x)
    except:
        return x

def normalize(x):
    if np.max(x) == np.min(x):
        return np.zeros_like(x)
    return (x - np.min(x)) / (np.max(x) - np.min(x))

def get_tip(level):
    if level == "LOW":
        return "You're doing great 😊"
    elif level == "MODERATE":
        return "Take a short break and breathe 💛"
    else:
        return "Take 3 slow deep breaths 🫁"


# -------------------------- UI -------------------------- #

st.title("🧠 Simple Real-Time Stress Dashboard")
st.write("Updates automatically every **3 seconds**")

placeholder = st.empty()

while True:
    df = fetch_data()

    if df.empty:
        st.warning("Waiting for data...")
        time.sleep(3)
        continue

    # 4Hz resampling for clean filtering
    df_rs = df.resample("250ms").mean().interpolate()

    # Apply filters
    df_rs["gsr_f"] = butter_filt_bandpass(df_rs["gsr"].values)
    df_rs["hr_f"]  = butter_filt_lowpass(df_rs["hr"].values)
    df_rs["temp_f"] = df_rs["temp"].values

    # Normalize for stress formula
    gsr_norm = normalize(df_rs["gsr_f"])[-1]
    hr_norm  = normalize(df_rs["hr_f"])[-1]
    temp_norm = normalize(df_rs["temp_f"])[-1]

    # Stress score formula you gave:
    stress_score = round(0.4*gsr_norm + 0.4*hr_norm + 0.2*temp_norm, 3)

    # Determine level
    if stress_score < 0.33:
        level = "LOW"
    elif stress_score < 0.66:
        level = "MODERATE"
    else:
        level = "HIGH"

    tip = get_tip(level)

    # SHOW IN DASHBOARD
    with placeholder.container():
        st.subheader("📌 Latest Stress Score")
        st.markdown(f"## **{stress_score}**")

        st.subheader("📊 Stress Level")
        st.markdown(f"### **{level}**")

        st.subheader("💡 Recommendation")
        st.write(f"**{tip}**")

        st.markdown("---")
        st.subheader("Recent Values")
        st.dataframe(df.tail(5))

    time.sleep(3)
