// Authored by Arash Harirpoosh - 9731505

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // Set the baud rate (115200 bits per second) of the Serial Monitor
  pinMode(LED_BUILTIN, OUTPUT);     // Initialize the LED_BUILTIN pin as an output
  pinMode(16, OUTPUT);     // Initialize GPIO16 pin as an output
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println("Hello World!!!"); // Print 'Hello World!!!' in Serial Monitor
  digitalWrite(LED_BUILTIN, LOW);   // Turn the LED on by making the voltage LOW
  digitalWrite(16, HIGH);  // Turn the LED off by making the voltage HIGH
  delay(1000);                      // Wait for a second
  digitalWrite(LED_BUILTIN, HIGH);  // Turn the LED off by making the voltage HIGH
  digitalWrite(16, LOW);   // Turn the LED on by making the voltage LOW
  delay(1000); // Wait for a second
}
