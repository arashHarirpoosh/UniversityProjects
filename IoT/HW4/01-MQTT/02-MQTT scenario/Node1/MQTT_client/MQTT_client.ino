
// Authored by Arash Harirpoosh - 9731505


#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>


#define RST_PIN D3      // RST RFID pin
#define SS_PIN  D4      // SDA RFID pin
#define waterSensorPin A0   // ESP8266 Analog Pin ADC0 = A0


MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
String tagID = "";


// Update these with values suitable for your network.

const char* ssid = "Arash";
const char* password = "12345678";
IPAddress mqtt_server (192, 168, 43, 113);
const int mqttPort = 1883;

const int heat_amount = 15; // PWM pin number of led that shows the required heat of water
const int led_water = 4; // Pin number of led that shows the amount of water
const int led_blink = 5; // Pin number of led that blinks before the required amount of water satisfied
float waterSensorValue;
float required_temprature = 0.2 * 1024;
float required_water = 0.1 * 1024;

WiFiClient espClient;
PubSubClient client(espClient);
//unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE  (50)
char msg[MSG_BUFFER_SIZE];
char letter;
String temp = "";
int num_of_seprators = 0;
boolean append = false;

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

void callback(char* topic, byte* payload, unsigned int length) {
  num_of_seprators = 0;
  for (int i = 0; i < length; i++) {
    letter = payload[i];

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

      }
      temp = "";
    }
    if (letter != ':' && append) {
      temp.concat(letter);
    }
  }
  Serial.println();
}

// Reconnect to the MQTT broker
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      //      client.publish("outTopic", "hello world");
      // ... and resubscribe
      client.subscribe("userInfo");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(heat_amount, OUTPUT); // Initialize GPIO15 pin as an output
  pinMode(led_water, OUTPUT);   // Initialize GPIO4 pin as an output
  pinMode(led_blink, OUTPUT);   // Initialize GPIO5 pin as an output
  pinMode(waterSensorPin, INPUT); // Initialize A0 pin as an input


  SPI.begin();            // Init SPI bus
  mfrc522.PCD_Init();     // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));


  setup_wifi();
  client.setServer(mqtt_server, mqttPort);
  client.setCallback(callback);
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

  if (!client.connected()) {
    reconnect();
  }

  client.loop();

  waterSensorValue = analogRead(waterSensorPin);       // Read the value of the water sensor and store it in 'waterSensorValue'
  analogWrite(heat_amount, required_temprature);    // Set the duty cycle of the built in LED
  //  analogWrite(led_water, required_water - waterSensorValue);    // Set the duty cycle of the built in LED
  analogWrite(led_water, waterSensorValue);    // Set the duty cycle of the built in LED

  // LED will turn of if the water level wasn't sifficient
  if (waterSensorValue < required_water + 50 and required_water - 50 < waterSensorValue) {
    digitalWrite(led_blink, LOW);

  }

  // LED will blink if the water level wasn't sifficient
  else {
    digitalWrite(led_blink, HIGH);
    delay(500);
    digitalWrite(led_blink, LOW);
    delay(500);
  }

  // If RFID detect a tag the tagID will be send to the server
  if (getID()) {
    Serial.println(tagID);
    tagID.toCharArray(msg, MSG_BUFFER_SIZE);
    Serial.print("Publish message: ");
    Serial.println(msg);
    client.publish("tagID", msg);

  }

}
