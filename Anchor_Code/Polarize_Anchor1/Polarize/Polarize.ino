#include <BLEPeripheral.h>
#include <iBeacon.h>
 
iBeacon beacon;
 
const int LED_RED = 23;
const int LED_GREEN = 24;
const int ANTENNA_SWITCH = 25;
 
char* uuid = "d8ac484e-4fbb-4b36-bf12-c249ab83673b";
unsigned short major = 888;
unsigned short minor = 201;
unsigned short measuredPower = -55;
 
bool isTransmitPhase = true;
 
BLEPeripheral blePeripheral = BLEPeripheral();
 
void setup() {
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(ANTENNA_SWITCH, OUTPUT);
 
  Serial.begin(115200);
  Serial.println(" เริ่มต้นระบบ ส่ง-รับ Beacon จริง");
 
  blePeripheral.setLocalName("n");  // BLEPeripheral ต้องตั้งชื่อไว้
  blePeripheral.begin();
}
 
void loop() {
  if (isTransmitPhase) {
    // === โหมดส่ง beacon ===
    digitalWrite(ANTENNA_SWITCH, HIGH);  // สลับไปเสาส่ง
    digitalWrite(LED_GREEN, HIGH);       // เขียว = ส่ง
    digitalWrite(LED_RED, LOW);
 
    beacon.begin(uuid, major, minor, measuredPower);
    Serial.println(" ส่ง beacon แล้ว!");
 
    delay(4000);  // ส่ง 4 วิ
    beacon.end();
  } else {
    // === โหมดรับ beacon ===
    digitalWrite(ANTENNA_SWITCH, LOW);   // สลับไปเสารับ
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);         // แดง = รับ
 
    Serial.println("🔍 เริ่มสแกนหา beacon...");
 
    BLECentral central = blePeripheral.central();
 
    if (central) {
      // พบอุปกรณ์ BLE
      Serial.print(" พบ beacon จากอุปกรณ์: ");
      Serial.println(central.address());
      Serial.println(" รับ beacon แล้ว!");
 
      // เปิด LED สองดวงแสดงผลชัดเจน
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(LED_RED, HIGH);
 
      delay(2000);
    }
  }
 
  isTransmitPhase = !isTransmitPhase;  // Toggle ส่ง/รับ
  delay(1000);  // เว้นช่วงก่อนสลับรอบ
}