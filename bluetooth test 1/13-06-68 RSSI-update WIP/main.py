from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
import time

load_framework(INCLUDE.Foundation)

BluetoothBridge = autoclass('BluetoothBridge')
NSDictionary = autoclass('NSDictionary')
NSData = autoclass('NSData')

class BluetoothGATTApp(App):

    def build(self):
        # สร้าง layout หลัก
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label สำหรับแสดงข้อมูล
        self.label = Label(text="Initializing Bluetooth GATT...", size_hint_y=0.6)
        
        # สร้าง buttons layout
        button_layout = BoxLayout(orientation='vertical', size_hint_y=0.4, spacing=5)
        
        # ปุ่มต่างๆ สำหรับ GATT operations
        scan_btn = Button(text="Start Scan", size_hint_y=None, height=40)
        scan_btn.bind(on_press=self.start_scan)
        
       

        connect_gatt_btn = Button(text="Connect GATT", size_hint_y=None, height=40)
        connect_gatt_btn.bind(on_press=self.connect_gatt)

        rssi_btn = Button(text="RSSI", size_hint_y=None, height=40)
        rssi_btn.bind(on_press=self.rssi_scan)


        stop_rssi_monitoring_btn = Button(text="stop_rssi_monitoring", size_hint_y=None, height=40)
        stop_rssi_monitoring_btn.bind(on_press=self.stop_rssi_monitoring)
        
        read_data_btn = Button(text="Read Data", size_hint_y=None, height=40)
        read_data_btn.bind(on_press=self.read_characteristic_data)
        
        write_data_btn = Button(text="Write Data", size_hint_y=None, height=40)
        write_data_btn.bind(on_press=self.write_characteristic_data)
        
        device_info_btn = Button(text="Device Info", size_hint_y=None, height=40)
        device_info_btn.bind(on_press=self.get_detailed_device_info)
        
        system_status_btn = Button(text="System Status", size_hint_y=None, height=40)
        system_status_btn.bind(on_press=self.get_system_status)
        
        # เพิ่มปุ่ม reconnect
        reconnect_btn = Button(text="Reconnect", size_hint_y=None, height=40)
        reconnect_btn.bind(on_press=self.smart_reconnect)
        
        auto_reconnect_btn = Button(text="Setup Auto Reconnect", size_hint_y=None, height=40)
        auto_reconnect_btn.bind(on_press=lambda x: self.setup_auto_reconnect())
        
        # เพิ่ม buttons ใน layout
        button_layout.add_widget(scan_btn)
        button_layout.add_widget(connect_gatt_btn)
        button_layout.add_widget(read_data_btn)
        button_layout.add_widget(write_data_btn)
        button_layout.add_widget(device_info_btn)
        button_layout.add_widget(system_status_btn)
        button_layout.add_widget(reconnect_btn)
        button_layout.add_widget(auto_reconnect_btn)
        button_layout.add_widget(rssi_btn) 
        button_layout.add_widget(stop_rssi_monitoring_btn) 
    
        
        # เพิ่มใน main layout
        main_layout.add_widget(self.label)
        main_layout.add_widget(button_layout)
        
        # สร้าง bridge และเริ่มต้น
        self.bridge = BluetoothBridge.alloc().init()
        self.current_device_uuid = None
        self.gatt_connected = False
        
        # เริ่ม scan อัตโนมัติ
        self.start_scan(None)
        
        Clock.schedule_interval(self.check_discovered_device, 1.0)
        return main_layout

    def start_scan(self, instance):
        """เริ่ม scan หา devices"""
        Logger.info("BluetoothGATTApp: Starting full device scan...")
        
        # ใช้ method ใหม่ที่มี cleanup
        self.bridge.performFullDeviceScan()
        self.update_label("Scanning for devices...")

    
        
    def connect_gatt(self, instance):
        """เชื่อมต่อ GATT กับ device ล่าสุด"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothGATTApp: Connecting GATT to device: {self.current_device_uuid}")
            
            # เรียกใช้ GATT connection method ใหม่
            self.bridge.startConnectionForDevice_(objc_str(self.current_device_uuid))
            
            # เริ่ม periodic RSSI updates
            self.bridge.startPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            self.gatt_connected = True
            self.update_label(f"GATT Connecting...\nDevice: {self.current_device_uuid}")
            
            # ตรวจสอบสถานะการเชื่อมต่อ
            Clock.schedule_once(self.check_connection_status, 3.0)
            self.bridge.stopBluetoothScan()
        else:
            self.update_label("No device found to connect GATT")

    def check_connection_status(self, dt):
        """ตรวจสอบสถานะการเชื่อมต่อ GATT"""
        if self.current_device_uuid:
            try:
                is_connected = self.bridge.isDeviceConnected_(objc_str(self.current_device_uuid))
                connection_state = self.bridge.getConnectionStateForDevice_(objc_str(self.current_device_uuid))
                
                Logger.info(f"Connection Status: {connection_state}, Connected: {is_connected}")
                
                if is_connected:
                    # ✅ ใช้ method ที่ง่ายกว่า
                    
                    
                    self.update_label(f"✅ GATT Connected!\nDevice: {self.current_device_uuid[:8]}...\nState: {connection_state}\n")
                    Clock.schedule_once(lambda dt: self.get_available_services(), 1.0)
                else:
                    self.update_label(f"❌ GATT Connection Failed\nState: {connection_state}")
                    
            except Exception as e:
                Logger.error(f"Error checking connection status: {e}")
                self.update_label(f"Connection check failed: {e}")

    def get_available_services(self):
        """ดึงรายการ services ที่มีใน device"""
        if self.current_device_uuid:
            try:
                # ✅ ใช้ method ที่ return [String]
                # service_uuids = self.bridge.getAvailableServicesForDevice_(objc_str(self.current_device_uuid))
                #service_names = self.bridge.getAvailableServicesWithNames_(objc_str(self.current_device_uuid))
                
                
                
                Logger.info(f"Service UUIDs: {service_uuids}")
               # Logger.info(f"Service Names: {service_names}")
                

            except Exception as e:
                Logger.error(f"Error getting services: {e}")
                self.update_label(f"Error getting services: {e}")
###############################################################
    def get_detailed_services(self):
        """ดึงข้อมูล services แบบละเอียด"""
        if self.current_device_uuid:
            try:
                # ✅ ใช้ method ที่ return string
                services_string = self.bridge.getAvailableServicesString_(objc_str(self.current_device_uuid))
                
                if services_string:
                    self.update_label(f"📋 Available Services:\n\n{services_string}")
                else:
                    self.update_label("No services available")
                    
            except Exception as e:
                Logger.error(f"Error getting detailed services: {e}")

    def display_service_details(self, instance):
        """แสดงรายละเอียด services"""
        if self.current_device_uuid:
            try:
                # ✅ ใช้ method ที่ return formatted string
                services_string = self.bridge.getAvailableServicesString_(objc_str(self.current_device_uuid))
                
                if services_string:
                    # แสดงใน popup หรือ label ใหม่
                    self.update_label(f"📋 Service Details:\n\n{services_string}")
                    
                    # Schedule กลับไปแสดงหน้าหลักหลัง 10 วินาที
                    Clock.schedule_once(lambda dt: self.get_available_services(), 10.0)
                else:
                    self.update_label("No service details available")
                    
            except Exception as e:
                Logger.error(f"Error displaying service details: {e}")
###############################################################
    def read_characteristic_data(self, instance):
        """อ่านข้อมูลจาก characteristic"""
        if not self.gatt_connected or not self.current_device_uuid:
            self.update_label("Please connect GATT first")
            return
        
        # ตัวอย่างการอ่านข้อมูลจาก Battery Service
        service_uuid = "180F"  # Battery Service
        characteristic_uuid = "2A19"  # Battery Level Characteristic
        
        Logger.info(f"Reading characteristic {characteristic_uuid} from service {service_uuid}")
        
        try:
            self.bridge.readCharacteristicForDevice_serviceUUID_characteristicUUID_(
                objc_str(self.current_device_uuid),
                objc_str(service_uuid),
                objc_str(characteristic_uuid)
            )
            
            self.update_label(f"Reading battery level...\nService: {service_uuid}\nCharacteristic: {characteristic_uuid}")
            
        except Exception as e:
            Logger.error(f"Error reading characteristic: {e}")
            self.update_label(f"Error reading data: {e}")

    def write_characteristic_data(self, instance):
        """เขียนข้อมูลไป characteristic"""
        if not self.gatt_connected or not self.current_device_uuid:
            self.update_label("Please connect GATT first")
            return
        
        # ตัวอย่างการเขียนข้อมูล string
        service_uuid = "FF10"  # Custom Service UUID
        characteristic_uuid = "FF11"  # Custom Characteristic UUID
        data_to_write = "Hello IoT Device!"
        
        Logger.info(f"Writing data: {data_to_write}")
        
        try:
            # เขียนข้อมูลแบบ string
            self.bridge.writeStringData_toDevice_serviceUUID_characteristicUUID_(
                objc_str(data_to_write),
                objc_str(self.current_device_uuid),
                objc_str(service_uuid),
                objc_str(characteristic_uuid)
            )
            
            self.update_label(f"Writing data: {data_to_write}\nTo service: {service_uuid}")
            
        except Exception as e:
            Logger.error(f"Error writing data: {e}")
            self.update_label(f"Error writing data: {e}")

    def write_hex_data_example(self):
        """ตัวอย่างการเขียนข้อมูล hex"""
        if not self.gatt_connected or not self.current_device_uuid:
            return
        
        # ตัวอย่างการเขียนข้อมูล hex (เช่น ควบคุม LED)
        service_uuid = "FF20"
        characteristic_uuid = "FF21"
        hex_data = "FF0000"  # Red color in RGB hex
        
        try:
            self.bridge.writeHexData_toDevice_serviceUUID_characteristicUUID_(
                hex_data,
                self.current_device_uuid,
                service_uuid,
                characteristic_uuid
            )
            
            Logger.info(f"Wrote hex data: {hex_data}")
            
        except Exception as e:
            Logger.error(f"Error writing hex data: {e}")

    def get_detailed_device_info(self, instance):
        """ดึงข้อมูลอุปกรณ์แบบละเอียด"""
        if self.current_device_uuid:
            try:
                # ✅ แก้ไขการเรียก method
                detailed_info = self.bridge.getDetailedDeviceInfo_(objc_str(self.current_device_uuid))
                
                if detailed_info:
                    name = detailed_info.objectForKey_(objc_str("name"))
                    state = detailed_info.objectForKey_(objc_str("state"))
                    services = detailed_info.objectForKey_(objc_str("services"))
                    characteristics = detailed_info.objectForKey_(objc_str("characteristics"))
                  
                    char_count = detailed_info.objectForKey_(objc_str("characteristicCount"))
                    
                    info_text = f"Device: {name}\n"
                    info_text += f"State: {state}\n"
                    
                    if services:
                        info_text += f"Services: {len(services)}\n"
                        for i, service in enumerate(services[:3]):  # แสดงแค่ 3 services แรก
                            service_uuid = service.objectForKey_(objc_str("uuid"))
                            info_text += f"  - {service_uuid}\n"
                    
                    if characteristics:
                        info_text += f"Characteristics: {len(characteristics)}"
                    
                    self.update_label(info_text)
                    Logger.info(f"Detailed device info displayed successfully")
                    
                else:
                    self.update_label("No detailed info available")
                    Logger.warning("No detailed device info returned")
                    
            except Exception as e:
                Logger.error(f"Error getting detailed info: {e}")
                self.update_label(f"Error: {e}")
        else:
            self.update_label("No device selected")

    def get_system_status(self, instance):
        """ดึงสถานะระบบทั้งหมด"""
        try:
            status = self.bridge.getFullSystemStatus()
            
            if status:
                is_scanning = status.objectForKey_(objc_str("isScanning"))
                connected_count = status.objectForKey_(objc_str("connectedDevicesCount"))
                total_discovered = status.objectForKey_(objc_str("totalDiscoveredDevices"))
                bluetooth_state = status.objectForKey_(objc_str("bluetoothState"))
                
                status_text = f"System Status:\n"
                status_text += f"Scanning: {bool(is_scanning.boolValue())}\n"
                status_text += f"Connected: {connected_count.intValue()}\n"
                status_text += f"Discovered: {total_discovered.intValue()}\n"
                status_text += f"Bluetooth: {bluetooth_state}\n"
                
                if self.current_device_uuid:
                    device_state = self.bridge.getConnectionStateForDevice_(objc_str(self.current_device_uuid))
                    status_text += f"Current Device: {device_state}"
                
                self.update_label(status_text)
                Logger.info("System status displayed successfully")
            else:
                self.update_label("Unable to get system status")
                Logger.warning("No system status returned")
                
        except Exception as e:
            Logger.error(f"Error getting system status: {e}")
            self.update_label(f"Status Error: {e}")

    @mainthread
    def update_label(self, text):
        """อัพเดท label text"""
        self.label.text = text

    @mainthread
    def check_discovered_device(self, dt):
        """เช็ค device ที่เจอใหม่"""
        device = self.bridge.getLastDiscoveredDevice()
        if device:
            name = device.objectForKey_(objc_str("name")).UTF8String()
            uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
            rssi = device.objectForKey_(objc_str("rssi")).intValue()
            major = device.objectForKey_(objc_str("major")).intValue()
            minor = device.objectForKey_(objc_str("minor")).intValue()

            # เก็บ UUID ล่าสุด
            self.current_device_uuid = uuid

            # แสดงข้อมูล device พร้อมสถานะ GATT
            display_text = f"Device: {name}\nUUID: {uuid}\nRSSI: {rssi}\nMajor: {major} Minor: {minor}"
            
            # เพิ่มข้อมูลสถานะ GATT
            if self.gatt_connected:
                connection_state = self.bridge.getConnectionStateForDevice_(objc_str(uuid))
                display_text += f"\nGATT State: {connection_state}"
            else:
                display_text += f"\nGATT: Not Connected"
            
            # เพิ่มข้อมูลสถานะระบบ
            connected_count = self.bridge.getConnectedDevicesCount()
            is_scanning = self.bridge.isScanning()
            
            display_text += f"\n\nSystem Status:"
            display_text += f"\nConnected: {connected_count}"
            display_text += f"\nScanning: {is_scanning}"
            
            self.label.text = display_text

    def on_stop(self):
        """หยุดการทำงานเมื่อปิด app"""
        Logger.info("BluetoothGATTApp: Stopping...")
        
        # หยุด RSSI monitoring
        if hasattr(self, 'rssi_monitoring') and self.rssi_monitoring:
            self.stop_rssi_monitoring()  # ← เรียกโดยไม่ส่ง parameter
        
        # หยุด RSSI updates
        if self.current_device_uuid:
            try:
                self.bridge.stopPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            except Exception as e:
                Logger.error(f"Error stopping RSSI updates: {e}")
        
        Logger.info("BluetoothGATTApp: Stopped and cleaned up")

    # เพิ่ม methods สำหรับการใช้งานขั้นสูง
    def test_all_gatt_methods(self):
        """ทดสอบ GATT methods ทั้งหมด"""
        Logger.info("BluetoothGATTApp: Testing all GATT methods...")
        
        if not self.current_device_uuid:
            Logger.warning("No device available for testing")
            return
        
        try:
            # Test 1: Validate UUID
            is_valid = self.bridge.validateUUID_(self.current_device_uuid)
            Logger.info(f"✅ UUID Validation: {is_valid}")
            
            # Test 2: Check connection state
            state = self.bridge.getConnectionStateForDevice_(self.current_device_uuid)
            Logger.info(f"✅ Connection State: {state}")
            
            # Test 3: Get detailed device info
            detailed_info = self.bridge.getDetailedDeviceInfoForUUID_(self.current_device_uuid)
            Logger.info(f"✅ Detailed Info Available: {detailed_info is not None}")
            
            # Test 4: Get system status
            system_status = self.bridge.getFullSystemStatus()
            Logger.info(f"✅ System Status Available: {system_status is not None}")
            
            Logger.info("✅ All GATT methods tested successfully")
            return True
            
        except Exception as e:
            Logger.error(f"❌ GATT method test failed: {e}")
            return False

    def connect_and_read_battery(self):
        """ตัวอย่างการเชื่อมต่อและอ่าน battery level"""
        if not self.current_device_uuid:
            self.update_label("No device available")
            return
        
        Logger.info("Starting battery reading process...")
        
        # Step 1: Connect GATT
        self.bridge.startConnectionForDevice_(self.current_device_uuid)
        self.update_label("Connecting GATT...")
        
        # Step 2: Schedule battery reading after connection
        Clock.schedule_once(self.read_battery_level, 3.0)

    def read_battery_level(self, dt):
        """อ่านค่า battery level"""
        try:
            # อ่านค่า battery จาก standard Battery Service
            self.bridge.readCharacteristicForDevice_serviceUUID_characteristicUUID_(
                self.current_device_uuid,
                "180F",  # Battery Service UUID
                "2A19"   # Battery Level Characteristic UUID
            )
            
            self.update_label("Reading battery level...")
            Logger.info("Battery level read request sent")
            
        except Exception as e:
            Logger.error(f"Error reading battery: {e}")
            self.update_label(f"Battery read error: {e}")

    def send_custom_command(self, command_data):
        """ส่งคำสั่งแบบกำหนดเองไปยังอุปกรณ์"""
        if not self.gatt_connected or not self.current_device_uuid:
            Logger.warning("GATT not connected")
            return
        
        # ตัวอย่างการส่งคำสั่งไปยัง custom service
        custom_service_uuid = "12345678-1234-1234-1234-123456789ABC"
        command_characteristic_uuid = "87654321-4321-4321-4321-CBA987654321"
        
        try:
            if isinstance(command_data, str):
                # ส่งข้อมูลแบบ string
                self.bridge.writeStringData_toDevice_serviceUUID_characteristicUUID_(
                    command_data,
                    self.current_device_uuid,
                    custom_service_uuid,
                    command_characteristic_uuid
                )
            else:
                # ส่งข้อมูลแบบ hex
                self.bridge.writeHexData_toDevice_serviceUUID_characteristicUUID_(
                    command_data,
                    self.current_device_uuid,
                    custom_service_uuid,
                    command_characteristic_uuid
                )
            
            Logger.info(f"Custom command sent: {command_data}")
            
        except Exception as e:
            Logger.error(f"Error sending custom command: {e}")

    def monitor_device_continuously(self):
        """ตรวจสอบอุปกรณ์อย่างต่อเนื่อง"""
        if self.current_device_uuid:
            # เริ่ม periodic monitoring
            Clock.schedule_interval(self.update_device_status, 2.0)
            Logger.info("Started continuous device monitoring")

    def update_device_status(self, dt):
        """อัพเดทสถานะอุปกรณ์"""
        if not self.current_device_uuid:
            return
        
        try:
            # ตรวจสอบสถานะการเชื่อมต่อ
            is_connected = self.bridge.isDeviceConnected_(objc_str(self.current_device_uuid))
            connection_state = self.bridge.getConnectionStateForDevice_(objc_str(self.current_device_uuid))
            
            # ดึงข้อมูล RSSI ปัจจุบัน
            current_rssi = self.bridge.getCurrentRSSIForDevice_(objc_str(self.current_device_uuid))
            
            # อัพเดท UI
            status_text = f"Device Monitoring:\n"
            status_text += f"Connected: {is_connected}\n"
            status_text += f"State: {connection_state}\n"
            status_text += f"RSSI: {current_rssi} dBm\n"
            status_text += f"UUID: {self.current_device_uuid[:8]}..."
            
            # ตรวจสอบว่าการเชื่อมต่อหลุดหรือไม่
            if not is_connected and self.gatt_connected:
                Logger.warning("Device disconnected unexpectedly")
                self.gatt_connected = False
                status_text += "\n⚠️ Connection Lost!"
            
            self.update_label(status_text)
            
        except Exception as e:
            Logger.error(f"Error updating device status: {e}")
##################################################################################################################################
    
  ####################***--หลัก Reconnect Method--#############################################
    def reconnect_device(self, instance):
        """Reconnect ไปยังอุปกรณ์ที่เคยเชื่อมต่อ"""
        if not self.current_device_uuid:
            self.update_label("❌ No device to reconnect")
            Logger.warning("No device UUID for reconnection")
            return
        
        try:
            Logger.info(f"🔄 Attempting to reconnect to device: {self.current_device_uuid}")
            
            # ✅ เรียกใช้ Swift reconnect method
            self.bridge.reconnectToDeviceWithUUID_(objc_str(self.current_device_uuid))
            
            self.update_label(f"🔄 Reconnecting...\nDevice: {self.current_device_uuid[:8]}...")
            
            # ตรวจสอบผลการ reconnect หลัง 3 วินาที
            Clock.schedule_once(self.check_reconnect_result, 3.0)
            
        except Exception as e:
            Logger.error(f"❌ Reconnect error: {e}")
            self.update_label(f"Reconnect Error: {e}")
###############################################################################################


####################***-- ตรวจสอบผล Reconnect--#################################################
    def check_reconnect_result(self, dt):
        """ตรวจสอบผลการ reconnect"""
        if not self.current_device_uuid:
            return
        
        try:
            is_connected = self.bridge.isDeviceConnected_(objc_str(self.current_device_uuid))
            connection_state = self.bridge.getConnectionStateForDevice_(objc_str(self.current_device_uuid))
            
            if is_connected:
                self.gatt_connected = True
                self.update_label(f"✅ Reconnect Successful!\nDevice: {self.current_device_uuid[:8]}...\nState: {connection_state}")
                Logger.info("✅ Device reconnected successfully")
                
                # เริ่ม RSSI updates อีกครั้ง
                self.bridge.startPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
                
            else:
                self.update_label(f"❌ Reconnect Failed\nState: {connection_state}\nTrying again...")
                Logger.warning("❌ Reconnect failed, will retry")
                
                # ลองอีกครั้งหลัง 2 วินาที
                Clock.schedule_once(lambda dt: self.reconnect_device(None), 2.0)
                
        except Exception as e:
            Logger.error(f"Error checking reconnect result: {e}")
    ###############################################################################################


####################***-- ตั้งค่า Auto Reconnect--#################################################
    def setup_auto_reconnect(self):
        """ตั้งค่า auto reconnect"""
        try:
            # ✅ เปิดใช้ auto reconnect ใน Swift
            self.bridge.setAutoReconnectEnabled_(True)
            
            # ✅ ตั้งค่าจำนวนครั้งที่ลองใหม่
            self.bridge.setMaxReconnectAttempts_(5)  # ลองใหม่ 5 ครั้ง
            
            Logger.info("✅ Auto reconnect enabled with 5 max attempts")
            
        except Exception as e:
            Logger.error(f"Error setting up auto reconnect: {e}")
    ###############################################################################################


####################***-- Reconnect พร้อม Retry Logic--#################################################
    def reconnect_with_retry(self, max_attempts=3):
        """Reconnect พร้อม retry logic ใน Python"""
        if not self.current_device_uuid:
            return
        
        self.reconnect_attempts = getattr(self, 'reconnect_attempts', 0)
        
        if self.reconnect_attempts >= max_attempts:
            self.update_label(f"❌ Max reconnect attempts ({max_attempts}) reached")
            Logger.error(f"Max reconnect attempts reached: {max_attempts}")
            self.reconnect_attempts = 0
            return
        
        self.reconnect_attempts += 1
        
        try:
            Logger.info(f"🔄 Reconnect attempt {self.reconnect_attempts}/{max_attempts}")
            
            # เรียกใช้ Swift reconnect
            self.bridge.reconnectToDeviceWithUUID_(objc_str(self.current_device_uuid))
            
            self.update_label(f"🔄 Reconnect Attempt {self.reconnect_attempts}/{max_attempts}\nDevice: {self.current_device_uuid[:8]}...")
            
            # ตรวจสอบผลหลัง 4 วินาที
            Clock.schedule_once(self.check_retry_reconnect_result, 4.0)
            
        except Exception as e:
            Logger.error(f"Reconnect attempt {self.reconnect_attempts} failed: {e}")
            # ลองใหม่หลัง 3 วินาที
            Clock.schedule_once(lambda dt: self.reconnect_with_retry(max_attempts), 3.0)
      ###############################################################################################

################***-- ตรวจสอบผล Retry--#################################################
    def check_retry_reconnect_result(self, dt):
        """ตรวจสอบผลการ reconnect แบบ retry"""
        if not self.current_device_uuid:
            return
        
        try:
            is_connected = self.bridge.isDeviceConnected_(objc_str(self.current_device_uuid))
            
            if is_connected:
                # สำเร็จ - รีเซ็ต attempts
                self.reconnect_attempts = 0
                self.gatt_connected = True
                self.update_label(f"✅ Reconnect Successful!\nAttempts used: {self.reconnect_attempts}\nDevice connected!")
                Logger.info("✅ Reconnect successful, attempts reset")
                
            else:
                # ไม่สำเร็จ - ลองใหม่
                Logger.warning(f"Reconnect attempt {self.reconnect_attempts} failed, retrying...")
                Clock.schedule_once(lambda dt: self.reconnect_with_retry(), 2.0)
                
        except Exception as e:
            Logger.error(f"Error checking retry result: {e}")
            Clock.schedule_once(lambda dt: self.reconnect_with_retry(), 2.0)

    def reconnect(self):
        """เก็บ method เดิมไว้เพื่อ compatibility"""
        Logger.info(f"Device reconnect requested...")
        
        if hasattr(self, '_device'):
            # ถ้ามี _device ให้เชื่อมต่อใหม่
            self.connect_gatt(self._device)
        elif self.current_device_uuid:
            # ใช้ reconnect method ใหม่
            self.reconnect_device(None)
        else:
            Logger.warning("No device available for reconnection")
            self.update_label("❌ No device to reconnect")

    def smart_reconnect(self, instance):
        """Smart reconnect ที่ตรวจสอบสถานะก่อน"""
        if not self.current_device_uuid:
            self.update_label("❌ No device selected")
            return
        
        try:
            # ตรวจสอบสถานะปัจจุบัน
            current_state = self.bridge.getConnectionStateForDevice_(objc_str(self.current_device_uuid))
            
            if current_state == "connected":
                self.update_label("✅ Device already connected!")
                return
            elif current_state == "connecting":
                self.update_label("🔄 Device is connecting...")
                return
            elif current_state == "disconnecting":
                self.update_label("⏳ Waiting for disconnection to complete...")
                Clock.schedule_once(lambda dt: self.smart_reconnect(None), 2.0)
                return
            else:  # disconnected
                Logger.info("Device disconnected, starting reconnection...")
                self.reconnect_with_retry(max_attempts=3)
                
        except Exception as e:
            Logger.error(f"Smart reconnect error: {e}")
            # Fallback ไปใช้ reconnect ธรรมดา
            self.reconnect_device(None)
    


    def rssi_scan(self, instance):
        """เริ่มการแสดง RSSI แบบ Real-time"""
        if not self.current_device_uuid:
            self.update_label("❌ No device found\nPlease scan for devices first")
            Logger.warning("No device available for RSSI check")
            return
        
        try:
            Logger.info(f"Starting real-time RSSI monitoring for: {self.current_device_uuid}")
            
            # ตรวจสอบว่ากำลัง monitor อยู่หรือไม่
            if hasattr(self, 'rssi_monitoring') and self.rssi_monitoring:
                # ถ้ากำลัง monitor อยู่ ให้หยุด
                #self.stop_rssi_monitoring()
                return
            
            # เริ่ม Real-time RSSI monitoring
            self.start_realtime_rssi_monitoring()
            
        except Exception as e:
            Logger.error(f"Error starting RSSI monitoring: {e}")
            self.update_label(f"❌ RSSI Monitor Error\n{str(e)}")

    def start_realtime_rssi_monitoring(self):
        """เริ่มการติดตาม RSSI แบบ Real-time"""
        try:
            # ตั้งค่า flag
            self.rssi_monitoring = True
            self.rssi_update_count = 0
            
            # เริ่ม periodic RSSI updates ใน Swift
            self.bridge.startPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            # Schedule การอัพเดท UI ทุก 1 วินาที
            self.rssi_monitor_event = Clock.schedule_interval(self.update_realtime_rssi, 1.0)
            
            # แสดงข้อความเริ่มต้น
            self.update_label("📶 Starting Real-time RSSI...\n🔄 Initializing...")
            
            Logger.info("✅ Real-time RSSI monitoring started")
            
        except Exception as e:
            Logger.error(f"Error starting real-time RSSI: {e}")
            self.rssi_monitoring = False

    def update_realtime_rssi(self, dt):
        """อัพเดท RSSI แบบ Real-time ทุกวินาที"""
        if not self.rssi_monitoring or not self.current_device_uuid:
            return False  # หยุด schedule
        
        try:
            # ดึงข้อมูล device ปัจจุบัน
            current_device = self.bridge.getCurrentDeviceInfo()
            print("Update")
            if current_device:
                name = current_device.objectForKey_(objc_str("name"))
                rssi = current_device.objectForKey_(objc_str("rssi"))
                uuid = current_device.objectForKey_(objc_str("uuid"))
                major = current_device.objectForKey_(objc_str("major"))
                minor = current_device.objectForKey_(objc_str("minor"))
                
                rssi_value = rssi.intValue() if rssi else -999
                
                if rssi_value != -999:
                    # เพิ่มตัวนับ
                    self.rssi_update_count += 1
                    
                    # ตรวจสอบการเปลี่ยนแปลง
                    if not hasattr(self, 'last_rssi') or self.last_rssi != rssi_value:
                        Logger.info(f"📶 RSSI Changed: {getattr(self, 'last_rssi', 'N/A')} → {rssi_value} dBm")
                        self.last_rssi = rssi_value
                    else:
                        Logger.info(f"📶 RSSI Same: {rssi_value} dBm")
            
                 
                    
                    # แสดงผล
                    current_time = time.strftime("%H:%M:%S")
                    
                    rssi_display = f"📶 RSSI Monitor (LIVE)\n"
                    rssi_display += f"━━━━━━━━━━━━━━━━━━━━\n"
                    rssi_display += f"🕐 Time: {current_time}\n"
                    rssi_display += f"📱 Device: {name.UTF8String() if name else 'Unknown'}\n"
                    rssi_display += f"🆔 UUID: {uuid.UTF8String()[:8] if uuid else 'N/A'}...\n"
                    rssi_display += f"📶 RSSI: {rssi_value} dBm\n"
           
                    rssi_display += f"🔢 Major: {major.intValue() if major else 0} | Minor: {minor.intValue() if minor else 0}\n"
                    rssi_display += f"━━━━━━━━━━━━━━━━━━━━\n"
                    rssi_display += f"🔄 Updates: {self.rssi_update_count}\n"
                    rssi_display += f"⏱️ Refreshing every 1s\n"
                    rssi_display += f"🛑 Tap RSSI again to stop"
                    
                    self.update_label(rssi_display)
                else:
                    Logger.warning("No valid RSSI value received")
            
            return True  # Continue scheduling
            
        except Exception as e:
            Logger.error(f"Error displaying RSSI: {e}")
            return True  # Continue แต่แสดง error

    def stop_rssi_monitoring(self, instance=None):  # ← เพิ่ม instance parameter
        """หยุดการติดตาม RSSI Real-time"""
        try:
            Logger.info("🛑 Stopping real-time RSSI monitoring...")
            
            # หยุด flag
            self.rssi_monitoring = False
            
            # หยุด Clock schedule
            if hasattr(self, 'rssi_monitor_event'):
                self.rssi_monitor_event.cancel()
                delattr(self, 'rssi_monitor_event')
            
            # หยุด periodic updates ใน Swift
            if self.current_device_uuid:
                self.bridge.stopPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            # แสดงข้อความหยุด
            final_count = getattr(self, 'rssi_update_count', 0)
            final_rssi = getattr(self, 'last_rssi', 'N/A')
            
            stop_message = f"📶 RSSI Monitor Stopped\n"
            stop_message += f"━━━━━━━━━━━━━━━━━━━━\n"
            stop_message += f"🕐 Stopped at: {time.strftime('%H:%M:%S')}\n"
            stop_message += f"📊 Total Updates: {final_count}\n"
            stop_message += f"📶 Last RSSI: {final_rssi} dBm\n"
            stop_message += f"━━━━━━━━━━━━━━━━━━━━\n"
            stop_message += f"✅ Monitoring stopped\n"
            stop_message += f"🔄 Tap RSSI to start again"
            
            self.update_label(stop_message)
            
            # ล้างตัวแปร
            if hasattr(self, 'rssi_update_count'):
                delattr(self, 'rssi_update_count')
            if hasattr(self, 'last_rssi'):
                delattr(self, 'last_rssi')
            
            Logger.info("✅ RSSI monitoring stopped successfully")
            
        except Exception as e:
            Logger.error(f"Error stopping RSSI monitoring: {e}")




def update_ui(self, name, rssi):
    scanned_info = f"{name}, RSSI: {rssi} dBm\nUUID: {self._uuid}\nMajor: {self._major}, Minor: {self._minor}"
    
    app = App.get_running_app()
    if app and hasattr(app.root, 'ids') and 'label' in app.root.ids:
        current_text = app.root.ids.label.text
        app.root.ids.label.text = scanned_info
    else:
        # fallback ถ้าไม่มี ids
        self.label.text = scanned_info



if __name__ == '__main__':
    app = BluetoothGATTApp()
    
    # ทดสอบ GATT methods หลังจากเริ่ม app
    def test_after_start():
        Clock.schedule_once(lambda dt: app.test_all_gatt_methods(), 5.0)
    
    test_after_start()
    app.run()