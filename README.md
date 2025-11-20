**Stress Monitoring System (ESP32 + IoT Dashboard)**

![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Hardware-ESP32-blue)
![Python](https://img.shields.io/badge/Backend-Python%203.10-yellow)
![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Active-success)

This project is an IoT-based real-time stress monitoring system built using ESP32, MAX30102, GSR v2.0, and DS18B20 sensors. 
The collected physiological signals (Heart Rate, SpO₂, Skin Conductance, Temperature) are logged to Google Sheets, processed in Google Colab, and visualized on a Streamlit dashboard.
The system performs FFT, FIR filtering, feature extraction (peak frequency, normalized values), and rule-based classification using weighted scores from HR, Temperature, and GSR to determine stress levels.

**Features**
Real-time data acquisition using ESP32
**Sensors used:**
MAX30102 → Heart Rate, SpO₂
GSR v2.0 → Skin Conductance
DS18B20 → Body Temperature

Automatic cloud logging using Google Sheets API
Signal processing in Google Colab
FFT
FIR Filtering
Feature Extraction
Rule-Based Stress Classification
Local Streamlit dashboard for visualization
Hardware + software integration for end-to-end monitoring

**System Architecture**
ESP32 reads sensor values
Sends data to Google Sheets
Colab accesses Sheets and processes data
Features are extracted
Rule-based algorithm computes stress score
Streamlit dashboard visualizes the stress level

**Repository Structure**
/esp32-code           → ESP32 firmware (sensor reading + data upload) 
/dashboard            → Streamlit dashboard code
/colab-processing     → FFT, FIR, feature extraction, stress rules
/hardware             → Circuit diagram / block diagram
README.md

**Technologies Used**
ESP32 (DIOT ESP32 Devkit V1)
MAX30102, GSR v2.0, DS18B20
Python (NumPy, SciPy)
Streamlit
Google Sheets API
Google Colab

**How It Works**
ESP32 collects physiological signals
Sends them to Google Sheets via Wi-Fi
Colab processes the data
A weighted scoring model (HR + Temp + GSR) gives stress output
Dashboard displays real-time and processed results
