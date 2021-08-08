
// Authored by Arash Harirpoosh - 9731505

#include <ESP8266WiFi.h>
#include "coap_client.h"
#include <SPI.h>
#include <MFRC522.h>


#define RST_PIN D3      // RST RFID pin
#define SS_PIN  D4      // SDA RFID pin
#define waterSensorPin A0   // ESP8266 Analog Pin ADC0 = A0


MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
String tagID = "";

//WiFi connection info
const char* ssid = "Arash";
const char* password = "12345678";

const int heat_amount = 15; // PWM pin number of led that shows the required heat of water
const int led_water = 4; // Pin number of led that shows the amount of water
const int led_blink = 5; // Pin number of led that blinks before the required amount of water satisfied
float waterSensorValue;
float required_temprature = 0.2 * 1024;
float required_water = 0.1 * 1024;

//instance for coapclient
coapClient coap;

//unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (20)
char msg[MSG_BUFFER_SIZE];
char letter;
String temp = "";
int num_of_seprators = 0;
boolean append = false;
boolean recieved_info = true;


//ip address and default port of coap server
IPAddress ip(192, 168, 43, 113);
int port = 5683;

// coap client response callback
void callback_response(coapPacket &packet, IPAddress ip, int port);

// coap client response callback
void callback_response(coapPacket &packet, IPAddress ip, int port) {
  char p[packet.payloadlen + 1];
  memcpy(p, packet.payload, packet.payloadlen);
  p[packet.payloadlen] = NULL;

  // Because it doesnt wait for response therfore it's possible to receive one response multiple times
  // So that we check that if we received it once dont process it again
    if (10 < packet.payloadlen and not recieved_info) {
//  if (10 < packet.payloadlen) {
    recieved_info = true;
    Serial.print("Response: ");
    Serial.println(p);
    // Reset the user requirements in server by sending pyt request
    int msgid = coap.put(ip, port, "userInfo", "", 1);
    num_of_seprators = 0;
    for (int i = 0; i < packet.payloadlen; i++) {
      letter = packet.payload[i];
      if (letter == ':') {
        num_of_seprators += 1;
        append = true;
      }
      else if (letter == ',') {
        append = false;
        if (num_of_seprators == 1) {
          Serial.print("Water level:");
          Serial.println(temp);
          required_water = (temp.toInt() / 100.0) * 1024;
          Serial.println(required_water);

        }

        else {
          Serial.print("Water temprature:");
          Serial.println(temp.toInt());
          required_temprature = (temp.toInt() / 100.0) * 1024;
          //                  Serial.println(required_temprature);
          //        Serial.println(temp.toInt() / 100.0);

        }
        temp = "";
      }
      if (letter != ':' && append) {
        temp.concat(letter);
      }
    }
  }
  Serial.println();

}

// Configure and connect to the network
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {

  Serial.begin(115200);

  pinMode(heat_amount, OUTPUT); // Initialize GPIO15 pin as an output
  pinMode(led_water, OUTPUT);   // Initialize GPIO4 pin as an output
  pinMode(led_blink, OUTPUT);   // Initialize GPIO5 pin as an output
  pinMode(waterSensorPin, INPUT); // Initialize A0 pin as an input

  delay(100);
  SPI.begin();            // Init SPI bus
  mfrc522.PCD_Init();     // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));


  setup_wifi();

  // client response callback.
  // this endpoint is single callback.
  coap.response(callback_response);

  // start coap client
  coap.start();

}

// Check whether the RFID detects tag or not and then save the tagID into the String variable
boolean getID()
{
  // Getting ready for Reading PICCs
  if ( ! mfrc522.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
    return false;
  }
  if ( ! mfrc522.PICC_ReadCardSerial()) { //Since a PICC placed get Serial and continue
    return false;
  }
  tagID = "";
  for ( uint8_t i = 0; i < 4; i++) { // The MIFARE PICCs that we use have 4 byte UID
    //readCard[i] = mfrc522.uid.uidByte[i];
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX)); // Adds the 4 bytes in a single String variable
  }
  tagID.toUpperCase();
  //  Serial.println(tagID);
  mfrc522.PICC_HaltA(); // Stop reading
  return true;
}


void loop() {
  bool state;

  state = coap.loop();
  waterSensorValue = analogRead(waterSensorPin);       // Read the value of the water sensor and store it in 'waterSensorValue'
  analogWrite(heat_amount, required_temprature);    // Set the duty cycle of the built in LED
  //  analogWrite(led_water, required_water - waterSensorValue);    // Set the duty cycle of the built in LED
  analogWrite(led_water, waterSensorValue);    // Set the duty cycle of the built in LED

  // LED will turn of if the water level wasn't sifficient
  if (waterSensorValue < required_water + 50 and required_water - 50 < waterSensorValue) {
    digitalWrite(led_blink, LOW);
    //    delay(1000);
    //    Serial.println(required_water);
    //    Serial.println(waterSensorValue);                    // Print the value of the 'waterSensorValue' in the Serial Monitor

  }

  // LED will blink if the water level wasn't sifficient
  else {
    //    Serial.println(waterSensorValue);                    // Print the value of the 'waterSensorValue' in the Serial Monitor

    digitalWrite(led_blink, HIGH);
    delay(500);
    digitalWrite(led_blink, LOW);
    delay(500);
  }
  // If RFID detect a tag the tagID will be send to the server
  if (getID()) {
    Serial.println(tagID);
    tagID.toCharArray(msg, MSG_BUFFER_SIZE);
    Serial.print("Request message: ");
    Serial.println(msg);
    // Send the tagID to the server via put request
    int msgid = coap.put(ip, port, "tagID", msg, MSG_BUFFER_SIZE);
    recieved_info = false;
  }
  delay(10);
  if (not recieved_info) {
    // Get the User requirements from server via get request
    int msgid = coap.get(ip, port, "userInfo");
    delay(500);
  }

}
