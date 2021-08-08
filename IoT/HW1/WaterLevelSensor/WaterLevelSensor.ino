// Authored by Arash Harirpoosh - 9731505

#define waterSensorPin A0   // ESP8266 Analog Pin ADC0 = A0
const int buzzerPin = 4;    // PWM pin number
int waterSensorValue;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);           // Set the baud rate (115200 bits per second) of the Serial Monitor
  pinMode(buzzerPin, OUTPUT);     // Initialize GPIO5 pin as an output
  pinMode(waterSensorPin, INPUT); // Initialize A0 pin as an input
  analogWriteRange(550);          // Change the range of PWM from the default value (1024) to 550

}

void loop() {
  // put your main code here, to run repeatedly:
  waterSensorValue = analogRead(waterSensorPin);       // Read the value of the water sensor and store it in 'waterSensorValue'
  Serial.println(waterSensorValue);                    // Print the value of the 'waterSensorValue' in the Serial Monitor
  analogWrite(buzzerPin, waterSensorValue);            // Set the duty cycle of the water sensor


}
