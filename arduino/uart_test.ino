#define RX_PIN 20
#define TX_PIN 21

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
}

void loop() {

  // Send test data
  Serial1.write("C");       // ASCII 'C' -> 0x43
  delay(500);

  Serial1.write(0xA4);       // Not a standard ASCII character
  delay(500);

  // Read all received ascii value bytes and converting to string
  while (Serial1.available()) {
    byte data = Serial1.read();

    Serial.print((char)data);
  }
}