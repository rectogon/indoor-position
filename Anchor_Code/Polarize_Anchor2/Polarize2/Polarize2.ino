/*
 * Project nRF51822 Two Antenna
 *
*/

#include <BLEPeripheral.h>
#include <iBeacon.h>

#if !defined(NRF51) && !defined(NRF52) && !defined(__RFduino__)
#error "This example only works with nRF51 boards"
#endif

iBeacon beacon;

boolean isLightOn = false;
const int LED_RED = 23;
const int LED_GREEN = 24;
const int PORT20 = 20;

// อัปเดตสถานะของ beacon ตามสถานะของ isLightOn
char* uuid = "A1111111-1111-1111-1111-111111111111";
unsigned short major = 111;  // กำหนดค่าเริ่มต้นให้ beacon ใช้เลย
unsigned short minor = 101;
unsigned short measuredPower = -55;

unsigned long lastSwitchTime = 0;
const unsigned long switchInterval = 5000;

void setup()
{
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(PORT20, OUTPUT);

  //กำหนดชื่อ iBeacon
  beacon.setLocalName("n1");
  beacon.begin(uuid, major, minor, measuredPower);  // เริ่ม beacon แค่ครั้งเดียวใน setup

  Serial.begin(9600);
  delay(1000);
  Serial.println("Beacon started...");
}

void loop()
{
  unsigned long currentTime = millis();

  if (currentTime - lastSwitchTime >= switchInterval) {
    lastSwitchTime = currentTime;
    isLightOn = !isLightOn;

    if (isLightOn) {
      major = 888;
      digitalWrite(PORT20, HIGH);
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(LED_RED, LOW);
      Serial.println("Switched to Antenna 2 (major = 888)");
    } else {
      major = 111;
      digitalWrite(PORT20, LOW);
      digitalWrite(LED_GREEN, LOW);
      digitalWrite(LED_RED, HIGH);
      Serial.println("Switched to Antenna 1 (major = 111)");
    }

    // ไม่ต้องเรียก beacon.begin() ซ้ำ
    // เพราะ Arduino core ตัวนี้ไม่ support การ re-start beacon ทุก loop
  }

  beacon.poll();  // ให้ BLE stack ทำงานใน background
}
