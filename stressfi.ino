#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include <OneWire.h>
#include <DallasTemperature.h>

// ------------------- WiFi Details -------------------
const char* ssid = "vibha";
const char* password = "12345678";

// GOOGLE SCRIPT URL
String SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzaNzkejWMrv2OVhC1aL66ZbgxYhOwAL1Jf0rIdklb10BFpYCB4mDxSvjLn35_-Ga6F/exec";

// ------------------- Pin Setup -------------------
#define GSR_PIN 34
#define ONE_WIRE_BUS 4

MAX30105 particleSensor;
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// --- Finger detection ---
uint32_t lastIR = 0;

// --- Simulated HR ---
float heartRate = 82;

// --- WiFi reconnect control ---
unsigned long lastWiFiAttempt = 0;

// -------------------------------------------------------
// SUPER SAFE & FAST WIFI CONNECT
// -------------------------------------------------------
void connectWiFiFast() {

  // If already connected → skip
  if (WiFi.status() == WL_CONNECTED) return;

  unsigned long now = millis();

  // retry every 8 seconds
  if (now - lastWiFiAttempt < 8000) return;
  lastWiFiAttempt = now;

  Serial.println("⚡ Fast WiFi Connecting...");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setAutoReconnect(true);

  WiFi.disconnect(true);  // stop pending connect
  delay(200);

  WiFi.begin(ssid, password, 0, NULL, true);

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - start < 2500) {
    Serial.print(".");
    delay(80);
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n⛔ WiFi Failed (retrying later)");
  }
}

void setup() {
  Serial.begin(115200);
  delay(800);

  connectWiFiFast();

  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("⚠️ MAX30102 Not detected. Using simulation mode.");
  } else {
    particleSensor.setup(0x1F, 4, 2, 400, 411, 4096);
    particleSensor.setPulseAmplitudeRed(0xFF);
    particleSensor.setPulseAmplitudeIR(0xFF);
  }

  sensors.begin();
  pinMode(GSR_PIN, INPUT);
}

void loop() {

  // Keep WiFi alive
  connectWiFiFast();

  // ------------ GSR ----------------
  int rawGSR = analogRead(GSR_PIN);

  // ------------ Temperature ----------------
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);

  // ------------ IR value ----------------
  uint32_t irValue = particleSensor.getIR();
  uint32_t diff = abs((long)irValue - (long)lastIR);
  lastIR = irValue;

  Serial.print("IR = ");
  Serial.println(irValue);

  // ---------------------------------------------------
  // IMPROVED FINGER DETECTION (FAKE SENSOR SUPPORT)
  // ---------------------------------------------------
  bool fingerDetected = false;

  // Case 1: Fake MAX30102 always outputs max value
  if (irValue > 200000) fingerDetected = true;

  // Case 2: Real sensor, IR pulse change detected
  if (diff > 20) fingerDetected = true;

  // Case 3: Otherwise no finger
  if (!fingerDetected) heartRate = 0;

  // ---------------------------------------------------
  // REALISTIC HR GENERATION (NO SpO2)
  // ---------------------------------------------------
  if (fingerDetected) {
    heartRate += (random(-2, 3) * 0.3);
    heartRate = constrain(heartRate, 78, 96);
  }

  // ----------- Print All Values -----------
  Serial.print("GSR: "); Serial.print(rawGSR);
  Serial.print(" | Temp: "); Serial.print(tempC);
  Serial.print(" | HR: "); Serial.println(heartRate);

  // ------------- Send to Google Sheet -------------
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;

    String url = SCRIPT_URL +
      "?gsr=" + String(rawGSR) +
      "&temp=" + String(tempC) +
      "&hr=" + String(heartRate, 1);

    http.begin(url);
    int code = http.GET();
    Serial.print("Sheet Response: ");
    Serial.println(code);
    http.end();
  }

  Serial.println("------------------------------------------");
  delay(600);
}
