// Authored by Arash Harirpoosh - 9731505

#include "ESP8266WiFi.h"

const char* ssid = "Arash";         // SSID of the network that nodemcu is going to connect to it
const char* password = "12345678"; // Password of the network that nodemcu is going to connect to it

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // Set the baud rate (115200 bits per second) of the Serial Monitor
  WiFi.mode(WIFI_STA);  // Set WiFi to station mode 
  WiFi.disconnect();    // Disconnect from an AP if it was previously connected
  delay(100);

  int numberOfNetworks = WiFi.scanNetworks(); // Scan and get the number of available wifi networks

  for (int i = 0; i < numberOfNetworks; i++) {
    // Print SSID and RSSI for each network found
    Serial.print("Network name: ");
    Serial.println(WiFi.SSID(i));
    Serial.print("Signal strength: ");
    Serial.println(WiFi.RSSI(i));
    Serial.println("-----------------------");

  }
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print("*");
  }

  Serial.println("");
  Serial.println("WiFi connection Successful");
  Serial.print("The IP Address of connected network: ");
  Serial.print(WiFi.localIP());// Print the IP address
}

void loop() {
  // put your main code here, to run repeatedly:

}
