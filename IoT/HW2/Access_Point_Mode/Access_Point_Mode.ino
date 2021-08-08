// Authored by Arash Harirpoosh - 9731505

#include <ESP8266WiFi.h>

const char *ssid = "NodeMCU";       // SSID of the nodemcu AP network
const char *password = "esp8266";   // Password of the nodemcu AP netwrok

void setup() {
  // put your setup code here, to run once:
  delay(100);
  Serial.begin(115200); // Set the baud rate (115200 bits per second) of the Serial Monitor
  Serial.println("Configuring access point...");
  WiFi.mode(WIFI_AP);          // Set WiFi to AccessPoint
  WiFi.softAP(ssid, password); // Set the SSID and password of the nodemcu AP network

  String ip_address = "AP IP address: " + WiFi.softAPIP().toString();
  Serial.println(ip_address); // Print the IP address of the network in the srial monitor
  // Static IP address configuration
  Serial.println("Set New Ap IP address...");
  IPAddress staticIP(192, 168, 1, 184); // ESP static ip
  IPAddress gateway(192, 168, 4, 9);    // ESP gateway
  IPAddress subnet(255, 255, 255, 0);   // ESP subnet mask
  WiFi.softAPConfig(staticIP, gateway, subnet); // Set the new IP address for nodemcu AP network

  String static_ip_address = "AP IP address: " + WiFi.softAPIP().toString();
  Serial.println(static_ip_address); // Print the new IP address of the network in the serial monitor
}

void loop() {
  // put your main code here, to run repeatedly:

}
