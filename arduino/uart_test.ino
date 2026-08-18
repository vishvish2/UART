#define RX_PIN 20
#define TX_PIN 21

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {

  // Send test data
  Serial1.write(0x43);
  delay(500);

  Serial1.write(0xA4);
  delay(500);

  // Read all received bytes
  while (Serial1.available()) {
    byte data = Serial1.read();

    Serial.print("RX: 0x");

    if (data < 0x10) {
      Serial.print("0");
    }

    Serial.println(data, HEX);
  }
}
