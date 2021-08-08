// Authored by Arash Harirpoosh - 9731505

#define ldrPin A0   // ESP8266 Analog Pin ADC0 = A0
const int buzzerPin = 5;  // PWM pin number
float ldrValue;
float ldrState;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // Set the baud rate (115200 bits per second) of the Serial Monitor
  pinMode(LED_BUILTIN, OUTPUT);   // Initialize the LED_BUILTIN pin as an output
  pinMode(buzzerPin, OUTPUT);     // Initialize GPIO5 pin as an output
  pinMode(ldrPin, INPUT);         // Initialize A0 pin as an input

}

void loop() {
  // put your main code here, to run repeatedly:
  ldrValue = analogRead(ldrPin);       // Read the value of the ldr sensor and store it in 'ldrValue'
  ldrState = (ldrValue / 1023) * 100;  // Cast the value of the ldr sensor into a number between 0 to 100
  Serial.println(ldrState);            // Print the value of the 'ldrState' in the Serial Monitor

  if (ldrState > 50) {
    digitalWrite(LED_BUILTIN, LOW);    // Turn the LED on by making the voltage LOW
    digitalWrite(buzzerPin, HIGH);     // Turn the buzzer on by making the voltage HIGH
  }
  else {
    digitalWrite(LED_BUILTIN, HIGH);   // Turn the LED off by making the voltage HIGH
    digitalWrite(buzzerPin, LOW);      // Turn the buzzer off by making the voltage LOW
  }

}
