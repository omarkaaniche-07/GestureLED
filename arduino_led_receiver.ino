const int LED_PINS[] = {2, 3, 4, 5};
const int NUM_LEDS = 4;

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(LED_PINS[i], OUTPUT);
    digitalWrite(LED_PINS[i], LOW);
  }
}

void loop() {
  if (Serial.available() > 0) {
    int number = Serial.parseInt();

    while (Serial.available() > 0) {
      Serial.read();
    }

    if (number >= 0 && number <= NUM_LEDS) {
      for (int i = 0; i < NUM_LEDS; i++) {
        digitalWrite(LED_PINS[i], i < number ? HIGH : LOW);
      }
    }
  }
}
