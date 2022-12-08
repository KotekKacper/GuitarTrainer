#define PERIOD 400 // microseconds

unsigned long last_us = 0L;

void setup() {
  Serial.begin (230400);
}

void loop() {
  // reading at a sample rate 1/PERIOD
  if (micros() - last_us > PERIOD){
    last_us += PERIOD;
    sample();
  }
}

void sample(){
  int sensorValue = analogRead(A0);
  // Convert the analog reading (which goes from 0 - 1023) to a voltage (0 - 5V):
  float voltage = sensorValue * (5.0 / 1023.0);
  Serial.println(voltage);
}
