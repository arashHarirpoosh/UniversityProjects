// Authored by Arash Harirpoosh - 9731505

#include <SPI.h>
#include <MFRC522.h>
#include <NTPClient.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define RST_PIN D3      // RST RFID pin
#define SS_PIN  D4      // SDA RFID pin

const int buzzer_pin = 4;  // Determine buzzer pin
const int led_pin = 5;      // Determine LED pin

const char* ssid = "Arash";         // SSID of the network that nodemcu is going to connect to it
const char* password = "12345678"; // Password of the network that nodemcu is going to connect to it

// Define NTP Client to get time
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(115200);   // Initialize serial communications with the PC
  pinMode(buzzer_pin, OUTPUT);   // Initialize GPIO4 pin as an output
  pinMode(led_pin, OUTPUT);      // Initialize GPIO5 pin as an output
  SPI.begin();            // Init SPI bus
  mfrc522.PCD_Init();     // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));

  WiFi.mode(WIFI_STA);  // Set WiFi to station mode 
  WiFi.disconnect();    // Disconnect from an AP if it was previously connected
  delay(100);
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print ("*");
  }
  
  Serial.println();
  Serial.println("WiFi connection Successful");
  timeClient.begin();  // Initialize the NTP client
  // Adjust the time for timezone in seconds
  // GMT +4.5 = 16200
  timeClient.setTimeOffset(16200);
}

void loop() {

  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if ( ! mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Dump debug info about the card; PICC_HaltA() is automatically called
  mfrc522.PICC_DumpToSerial(&(mfrc522.uid));

  timeClient.update();    // Get the current date and time from the NTP server
  String formattedTime = timeClient.getFormattedTime(); // Returns the time in HH:MM:SS format
  int currentHour = timeClient.getHours();              // Get the hours
  Serial.print("Formatted Time: ");
  Serial.println(formattedTime);
  if (9 < currentHour && currentHour < 16) {
    digitalWrite(led_pin, HIGH); // Turn the LED on by making the voltage HIGH
    delay(3000);
    digitalWrite(led_pin, LOW);  // Turn the LED off by making the voltage LOW
  }
  else {
    digitalWrite(buzzer_pin, HIGH); // Turn the buzzer on by making the voltage HIGH
    delay(3000);
    digitalWrite(buzzer_pin, LOW);  // Turn the buzzer off by making the voltage LOW
  }
}
