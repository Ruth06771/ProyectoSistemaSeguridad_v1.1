ESP32 -> Flask API example

This document shows a minimal Arduino (ESP32) example that sends an access event to the server.

Prerequisites
- Your Flask backend must be reachable from the ESP32 (same Wi-Fi network or public IP + NAT).
- If running locally on your dev machine, ensure firewall allows inbound requests on the Flask port (default 5000) and use your machine's LAN IP (e.g., 192.168.1.20).

Arduino (ESP32) example (Arduino IDE or PlatformIO):

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// IP/host of your machine running Flask
const char* serverHost = "http://192.168.1.100:5000"; // <- change this

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");

  // Example data
  const char* uid = "UID123456";
  const char* device = "Controladora-1";

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverHost) + "/api/esp/access";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<200> doc;
    doc["uid"] = uid;
    doc["device"] = device;
    doc["timestamp"] = "2025-10-07T12:34:56Z";

    String body;
    serializeJson(doc, body);

    int code = http.POST(body);
    String resp = http.getString();
    Serial.printf("POST %s -> %d\nResponse: %s\n", url.c_str(), code, resp.c_str());
    http.end();
  }
}

void loop() {
  // Nothing here
}
```

Testing with curl from a PC (replace host/IP):

```bash
curl -X POST http://192.168.1.100:5000/api/esp/access -H "Content-Type: application/json" -d '{"uid":"UID123456","device":"Controladora-1","timestamp":"2025-10-07T12:34:56Z"}'
```

Firewall/Network notes:
- If Flask runs on Windows, add an inbound firewall rule to allow `python.exe` or port 5000.
- If your machine uses a router, forward port 5000 to the machine running Flask or connect both ESP32 and machine to the same LAN.

Security note:
- The endpoint currently accepts unauthenticated posts from devices. For production protect with an API key or mutual TLS and validate device identities.
