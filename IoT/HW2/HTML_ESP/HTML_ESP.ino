// Authored by Arash Harirpoosh - 9731505

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

/* Put your SSID & Password */
const char* ssid = "NodeMCU";       // Enter SSID here
const char* password = "12345678";  // Enter Password here

/* Put IP Address details */
IPAddress local_ip(192, 168, 1, 1);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);

ESP8266WebServer server(80);    // Declare an object of ESP8266WebServer library

#define ldrPin A0       // ESP8266 Analog Pin ADC0 = A0
const int LEDpin = 5;   // LED pin number
bool LEDstatus = LOW;   // Store the status of the LED
float ldrValue;
float ldrState;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);       // Set the baud rate (115200 bits per second) of the Serial Monitor
  pinMode(LEDpin, OUTPUT);    // Initialize GPIO5 pin as an output
  pinMode(ldrPin, INPUT);     // Initialize A0 pin as an input

  WiFi.mode(WIFI_AP);                             // Turn the WiFi module(ESP8266) into an access point mode
  WiFi.softAP(ssid, password);                    // Set up a soft access point to establish a Wi-Fi network by proving ssid and password
  WiFi.softAPConfig(local_ip, gateway, subnet);   // Configure the IP address, IP subnet mask and IP gateway of the soft access point
  delay(500);

  server.on("/", handle_OnConnect);                   // Specify a handler for the root URL
  server.on("/updateLDR", handle_Update_ldr_value);   // Specify a handler for the /updateLDR URL
  server.on("/ledon", handle_ledon);                  // Specify a handler for the ledon URL
  server.onNotFound(handle_NotFound);                 // Specify a handler for other URL's

  server.begin();   // Start the server
  Serial.println("HTTP server started");
}

void loop() {
  // put your main code here, to run repeatedly:
  server.handleClient();
  digitalWrite(LEDpin, LEDstatus);   // Turn the LED on or off corresponding to the LEDstatus

}

// This is the handler of the root URL which turns off the led by making the status LOW
void handle_OnConnect() {
  LEDstatus = LOW;
  Serial.println("LED Status: OFF");
  server.send(200, "text/html", ConstructHTMLResponse(LEDstatus, ldrState)); // Send corresponding Http response
}

// This is the handler of the updateLDR URL which updates the value of the ldr sensor in the HTML page
void handle_Update_ldr_value() {
  ldrValue = analogRead(ldrPin);       // Read the value of the ldr sensor and store it in 'ldrValue'
  ldrState = (ldrValue / 1023) * 100;  // Cast the value of the ldr sensor into a number between 0 to 100
  Serial.println("Updated LDR Value is: " + String(ldrState));
  server.send(200, "text/html", ConstructHTMLResponse(LEDstatus, ldrState));  // Send corresponding Http response
}

// This is the handler of the ledon URL which turns on the led by making the status HIGH
void handle_ledon() {
  LEDstatus = HIGH;
  Serial.println("LED Status: ON");
  server.send(200, "text/html", ConstructHTMLResponse(LEDstatus, ldrState));  // Send corresponding Http response
}

// This is the handler of the other URL's
void handle_NotFound() {
  server.send(404, "text/plain", "Not found");
}

// Generating the Webpage for http response
String ConstructHTMLResponse(uint8_t ledstate, float ldrvalue) {
  String checkstatus;
  String temp = "<!DOCTYPE html>";
  temp += "<html lang=\"en\">";
  temp += "<head><meta charset=\"UTF-8\"><title>HTML&ESP</title></head>";
  temp += "<style>\\h1 {text-align: center;color: whitesmoke;margin: 45px;}";
  temp += "body {background-color: slategray;}";
  temp += ".button {border: None;border-radius: 50%;background-color: #4CAF50;color: black;padding: 16px 32px;";
  temp += "text-align: center;text-decoration: none;position: relative;top: 50%;left: 50%;transform: translate(-50%, -50%);";
  temp += "display: block;font-size: 16px;margin: 15px 2px;transition-duration: 0.4s;cursor: pointer;width: 225px;}";
  temp += ".button:hover {background-color: midnightblue;color: white;}";
  temp += ".button:active {background-color: black;color: whitesmoke;}.button-clicked {background-color: black;color: whitesmoke}";
  temp += ".text_status {text-align: center;}</style>";
  temp += "<body> <h1>HTM & ESP Practice</h1>";
  temp += "<a class=\"button\" href=\"/updateLDR\">Update LDR Value</a>";
  temp += "<a class=\"button\" href=\"/ledon\">Turn On The LED</a><a class=\"button\" href=\"/\">Turn Off The LED</a>";
  temp += "<div class=\"text_status\">";
  if (ledstate) {
    checkstatus = "ON";
  }
  else {
    checkstatus = "OFF";
  }
  temp += "LDR Value: " + String(ldrvalue) + "% <br><br> LED Status: " + checkstatus + "</div>";
  temp += "</body></html>";

  return temp;
}
