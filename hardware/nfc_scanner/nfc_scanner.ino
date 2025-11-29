#include <WiFiEsp.h>
#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_PN532.h>
#include <ArduinoJson.h>

// ================= CONFIGURATION =================
char ssid[] = "Galaxy S21";            // Phone Hotspot Name
char pass[] = "viul8161";        // Phone Hotspot Password
char server[] = "172.23.70.143";            // Your Laptop's IP (Run ipconfig/ifconfig)
int port = 5000;                           // Flask Port

// Must match the IOT_DEVICE_SECRET in your backend/.env
const char* deviceSecret = "Hospital-Scanner-Unit-V1-X99"; 
// =================================================

// Hardware Definitions
// ESP8266 TX -> Pin 2, ESP8266 RX -> Pin 3
SoftwareSerial SerialESP(2, 3); 

// PN532 I2C (SDA -> A4, SCL -> A5)
#define PN532_IRQ   (2)
#define PN532_RESET (3)
Adafruit_PN532 nfc(PN532_IRQ, PN532_RESET);

WiFiEspClient client;
int status = WL_IDLE_STATUS;

void setup() {
  Serial.begin(115200);   // Debugging via USB cable
  
  // 1. Initialize ESP8266
  // NOTE: Most ESPs default to 115200. SoftwareSerial on Uno is unstable at 115200.
  // If this freezes, you might need to change your ESP's baud rate to 9600.
  SerialESP.begin(9600); 
  WiFi.init(&SerialESP);

  // Check for ESP Hardware
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("Error: ESP8266 not detected. Check Wiring.");
    while (true);
  }

  // 2. Connect to WiFi
  while (status != WL_CONNECTED) {
    Serial.print("Connecting to WiFi: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
  }
  
  Serial.println("WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // 3. Initialize NFC
  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.print("Error: PN53x board not found. Check Wiring.");
    while (1); 
  }
  nfc.SAMConfig(); // Configure board to read RFID tags
  Serial.println("System Ready. Waiting for NFC Card...");
}

void loop() {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;

  // Listen for NFC Tag
  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Tag Detected!");
    
    // Convert Raw UID bytes to Hex String
    String uidString = "";
    for (uint8_t i = 0; i < uidLength; i++) {
       uidString += String(uid[i], HEX);
    }
    
    Serial.print("UID: "); Serial.println(uidString);
    sendDataToBackend(uidString);
    
    // Delay to prevent spamming the server
    delay(3000); 
  }
}

void sendDataToBackend(String uid) {
  if (client.connect(server, port)) {
    Serial.println("Connected to Server...");
    
    // 1. Prepare JSON Payload
    StaticJsonDocument doc;
    doc["uid"] = uid;
    String requestBody;
    serializeJson(doc, requestBody);

    // 2. Send HTTP POST Request
    client.println("POST /api/nfc/scan HTTP/1.1"); // Ensure this path matches Flask
    client.print("Host: "); client.println(server);
    client.println("Content-Type: application/json");
    client.print("X-Device-API-Key: "); client.println(deviceSecret);
    client.print("Content-Length: "); client.println(requestBody.length());
    client.println(); // Header/Body Separator
    client.println(requestBody);

    Serial.println("Data Sent.");
  } else {
    Serial.println("Connection Failed.");
  }
  client.stop();
}