// Authored by Arash Harirpoosh - 9731505

int led_pin[] = {0, 4, 5};  // LED pin's
int counter = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200); // Set the baud rate (115200 bits per second) of the Serial Monitor
  for (int i = 0; i < 3; i++) {
    pinMode(led_pin[i], OUTPUT); // Initialize GPIO0, 4, 5 pin as an output
  }

}

void showNum(int num) {
  for (int i = 0; i < 3; i++) {
    // Check the status of the i'th bit in num
    if (bitRead(num, i) == 1) {
      digitalWrite(led_pin[i], HIGH); // Turn the LED on by making the voltage HIGH if corresponding bit is 1
    }
    else {
      digitalWrite(led_pin[i], LOW);  // Turn the LED off by making the voltage LOW if corresponding bit is 0
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(1000); // Wait for a second
  Serial.println(counter); // Print the counter number in the Serial Monitor
  showNum(counter); // Display the input number with LED's
  counter += 1; // Increase the counter
  if (counter == 8) {
    counter = 0; // Reset the counter
  }
}
