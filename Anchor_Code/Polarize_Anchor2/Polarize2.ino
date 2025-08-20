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
char* uuid = "d8ac484e-4fbb-4b36-bf12-c249ab83673b";
unsigned short major;
unsigned short minor = 201;
unsigned short measuredPower = -55;

void setup() 
{
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(PORT20, OUTPUT);

  //กำหนดชื่อ iBeacon
  beacon.setLocalName("n");
}

void loop() 
{ 
  digitalWrite(LED_GREEN, isLightOn);

  if (isLightOn) {
    major = 888;
    digitalWrite(PORT20, LOW);
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_RED, LOW);
  } else {
    major = 111;
    digitalWrite(PORT20, HIGH);
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_RED, HIGH);
  }
  beacon.begin(uuid, major, minor, measuredPower);

//  delay(1000);
  isLightOn = !isLightOn;
  delay(5000);

  sd_ble_gap_adv_stop();
}
