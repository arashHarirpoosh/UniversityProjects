
#define ldrPin A0     // ESP8266 Analog Pin ADC0 = A0 
const int pwmPin = 4; // PWM pin number
int ldrValue;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);       // Set the baud rate (115200 bits per second) of the Serial Monitor
  pinMode(pwmPin, OUTPUT);    // Initialize GPIO4 pin as an output
  pinMode(ldrPin, INPUT);     // Initialize A0 pin as an input

}

void loop() {
  // put your main code here, to run repeatedly:
  ldrValue = analogRead(ldrPin);    // Read the value of the ldr sensor and store it in 'ldrValue'
  Serial.println(ldrValue);         // Print the value of the ldr sensor in the Serial Monitor
  analogWrite(pwmPin, ldrValue);    // Set the duty cycle of the built in LED

}
