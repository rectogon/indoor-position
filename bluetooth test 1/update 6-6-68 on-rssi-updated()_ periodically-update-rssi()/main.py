from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.logger import Logger

load_framework(INCLUDE.Foundation)

BluetoothBridge = autoclass('BluetoothBridge')
NSDictionary = autoclass('NSDictionary')

class BluetoothScanApp(App):
    
    # ย้าย method ขึ้นมาก่อน build()
    def clear_device_data(self, instance):
        """Clear ข้อมูล device ทั้งหมด"""
        Logger.info("BluetoothApp: Clearing device data...")
        self.current_device_uuid = None
        self.update_label("🗑️ All device data cleared")

    def build(self):
        # สร้าง layout หลัก
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label สำหรับแสดงข้อมูล device
        self.label = Label(text="Initializing Bluetooth...", size_hint_y=0.6)
        main_layout.ids = {'label': self.label}
        
        # สร้าง buttons layout แถวแรก
        button_layout1 = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        
        scan_btn = Button(text="Start Scan")
        scan_btn.bind(on_press=self.start_scan)
        
        stop_btn = Button(text="Stop Scan")
        stop_btn.bind(on_press=self.stop_scan)
        
        connect_btn = Button(text="Connect")
        connect_btn.bind(on_press=self.connect_device)
        
        button_layout1.add_widget(scan_btn)
        button_layout1.add_widget(stop_btn)
        button_layout1.add_widget(connect_btn)
        
        # สร้าง buttons layout แถวสอง
        button_layout2 = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=5)
        
        reconnect_btn = Button(text="Reconnect")
        reconnect_btn.bind(on_press=self.reconnect_device)
        
        rssi_btn = Button(text="Start RSSI")
        rssi_btn.bind(on_press=self.start_rssi_monitoring)
        
        info_btn = Button(text="Get Info")
        info_btn.bind(on_press=self.get_device_info)
        
        stop_rssi_btn = Button(text="Stop RSSI")
        stop_rssi_btn.bind(on_press=lambda x: self.stop_rssi_monitoring())
        
        # เพิ่มปุ่ม Clear
        clear_btn = Button(text="Clear Data")
        clear_btn.bind(on_press=lambda x: self.clear_data())
        
        button_layout2.add_widget(reconnect_btn)
        button_layout2.add_widget(rssi_btn)
        button_layout2.add_widget(info_btn)
        button_layout2.add_widget(stop_rssi_btn)
        button_layout2.add_widget(clear_btn)
        
        # เพิ่มใน main layout
        main_layout.add_widget(self.label)
        main_layout.add_widget(button_layout1)
        main_layout.add_widget(button_layout2)
        
        # สร้าง bridge และเริ่มต้น
        self.bridge = BluetoothBridge.alloc().init()
        self.current_device_uuid = None
        
        # เพิ่มตัวแปรสำหรับเก็บข้อมูล device
        self._uuid = ""
        self._major = 0
        self._minor = 0
        self._rssi = 0
        self._name = ""
        
        # เริ่ม scan อัตโนมัติ
        self.start_scan(None)
        
        Clock.schedule_interval(self.check_discovered_device, 1.0)
        return main_layout

    def clear_data(self):
        """Clear ข้อมูล device ทั้งหมด (ไม่รับ parameter)"""
        Logger.info("BluetoothApp: Clearing device data...")
        
        try:
            self.bridge.clearDiscoveredDevices()
        except:
            Logger.info("clearDiscoveredDevices method not available")
        
        self.current_device_uuid = None
        self._uuid = ""
        self._major = 0
        self._minor = 0
        self._rssi = 0
        self._name = ""
        
        self.update_label("🗑️ All device data cleared")

    def start_scan(self, instance):
        """เริ่ม scan หา devices"""
        Logger.info("BluetoothApp: Starting scan...")
        
        # Clear ข้อมูลเก่าก่อนเริ่ม scan ใหม่
        self.bridge.clearDiscoveredDevices()
        self.current_device_uuid = None
        
        self.bridge.startBluetoothScan()
        self.update_label("🔍 Scanning for devices...")

    def stop_scan(self, instance):
        """หยุด scan"""
        Logger.info("BluetoothApp: Stopping scan...")
        self.bridge.stopBluetoothScan()
        
        # Clear ข้อมูล device ปัจจุบัน
        self.current_device_uuid = None
        self._uuid = ""
        self._major = 0
        self._minor = 0
        self._rssi = 0
        self._name = ""
        
        self.update_label("🛑 Scan stopped\nDevice data cleared")

    def connect_device(self, instance):
        """เชื่อมต่อกับ device ล่าสุดที่เจอ"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothApp: Connecting to device: {self.current_device_uuid}")
            
            # แก้ไข: ใช้ objc_str() เพื่อแปลง Python string เป็น NSString
            uuid_nsstring = objc_str(self.current_device_uuid)
            self.bridge.connectToDeviceWithUUID_(uuid_nsstring)
            
            self.update_label(f"Connecting to device...\nUUID: {self.current_device_uuid}")
        else:
            self.update_label("No device found to connect")

    def reconnect_device(self, instance):
        """ทดสอบ reconnect method ใหม่"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothApp: Testing reconnect to device: {self.current_device_uuid}")
            
            # แก้ไข: ใช้ objc_str() เพื่อแปลง Python string เป็น NSString
            uuid_nsstring = objc_str(self.current_device_uuid)
            self.bridge.reconnectToDeviceWithUUID_(uuid_nsstring)
            
            self.update_label(f"Testing reconnect...\nUUID: {self.current_device_uuid}")
        else:
            self.update_label("No device found to reconnect")

    def start_rssi_monitoring(self, instance):
        """เริ่ม RSSI monitoring สำหรับ device ปัจจุบัน"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothApp: Starting RSSI monitoring for: {self.current_device_uuid}")
            
            try:
                uuid_nsstring = objc_str(self.current_device_uuid)
                
                # ใช้ method ที่เพิ่งสร้าง
                self.bridge.startRSSIUpdatesForDevice_(uuid_nsstring)
                self.update_label(f"📶 RSSI monitoring started\nDevice: {self._name}")
                
                # Schedule periodic RSSI checks
                Clock.schedule_interval(self.check_rssi_updates, 2.0)
                
            except Exception as e:
                Logger.error(f"Error starting RSSI monitoring: {e}")
                self.update_label(f"RSSI monitoring error: {e}")
        else:
            self.update_label("No device found for RSSI monitoring")

    def check_rssi_updates(self, dt):
        """เช็ค RSSI updates"""
        if self.current_device_uuid:
            try:
                uuid_nsstring = objc_str(self.current_device_uuid)
                current_rssi = self.bridge.getCurrentRSSIForDevice_(uuid_nsstring)
                
                if current_rssi != -999:  # Not error value
                    self._rssi = current_rssi
                    self.update_ui(self._name, current_rssi)
                    Logger.info(f"RSSI updated: {current_rssi} dBm")
                    
            except Exception as e:
                Logger.error(f"Error checking RSSI: {e}")

    def stop_rssi_monitoring(self):
        """หยุด RSSI monitoring"""
        if self.current_device_uuid:
            try:
                uuid_nsstring = objc_str(self.current_device_uuid)
                self.bridge.stopRSSIUpdatesForDevice_(uuid_nsstring)
                Clock.unschedule(self.check_rssi_updates)
                Logger.info("RSSI monitoring stopped")
            except Exception as e:
                Logger.error(f"Error stopping RSSI monitoring: {e}")

    def get_device_info(self, instance):
        """ดึงข้อมูล device ปัจจุบันทั้งหมด"""
        try:
            # ใช้ forced method เพื่อดึงข้อมูลแม้ไม่ได้ scan
            device = self.bridge.getLastDiscoveredDeviceForced()
            
            if device:
                name = device.objectForKey_(objc_str("name")).UTF8String()
                uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
                rssi = device.objectForKey_(objc_str("rssi")).intValue()
                major = device.objectForKey_(objc_str("major")).intValue()
                minor = device.objectForKey_(objc_str("minor")).intValue()
                
                # แสดงข้อมูลแบบละเอียด
                info_text = f"📱 Last Device Information:\n"
                info_text += f"Name: {name}\n"
                info_text += f"UUID: {uuid}\n"
                info_text += f"📶 RSSI: {rssi} dBm\n"
                info_text += f"Major: {major}\n"
                info_text += f"Minor: {minor}\n"
                
                # เพิ่มข้อมูลสถานะ
                connected_count = self.bridge.getConnectedDevicesCount()
                is_scanning = self.bridge.isScanning()
                has_devices = self.bridge.hasDiscoveredDevices()
                
                info_text += f"\n🔗 Connected: {connected_count}\n"
                info_text += f"🔍 Scanning: {is_scanning}\n"
                info_text += f"📋 Has Data: {has_devices}"
                
                self.update_label(info_text)
                Logger.info(f"Device info retrieved: {info_text}")
            else:
                self.update_label("📭 No device information available")
                
        except Exception as e:
            Logger.error(f"Error getting device info: {e}")
            self.update_label(f"Error: {e}")

    @mainthread
    def update_ui(self, name, rssi):
        """อัพเดท UI ด้วยข้อมูล device ใหม่ (รวม RSSI)"""
        # อัพเดทข้อมูลปัจจุบัน
        self._name = name
        self._rssi = rssi
        
        # สร้าง formatted string
        scanned_info = f"📱 {name}\n📶 RSSI: {rssi} dBm\n🆔 UUID: {self._uuid}\n📍 Major: {self._major}, Minor: {self._minor}"
        
        # เพิ่มข้อมูลสถานะ
        try:
            connected_count = self.bridge.getConnectedDevicesCount()
            is_scanning = self.bridge.isScanning()
            scanned_info += f"\n\n🔗 Connected: {connected_count}\n🔍 Scanning: {is_scanning}"
        except:
            pass
        
        app = App.get_running_app()
        if app and hasattr(app.root, 'ids') and 'label' in app.root.ids:
            app.root.ids.label.text = scanned_info
        else:
            self.label.text = scanned_info
        
        Logger.info(f"UI Updated with RSSI: {name} - {rssi} dBm")

    @mainthread
    def update_label(self, text):
        """อัพเดท label text"""
        self.label.text = text

    @mainthread
    def check_discovered_device(self, dt):
        """เช็ค device ที่เจอใหม่"""
        # เช็คว่ากำลัง scan อยู่หรือไม่
        is_scanning = self.bridge.isScanning()
        
        if not is_scanning:
            # ถ้าไม่ได้ scan อยู่ ไม่ต้องเช็ค device
            return
        
        device = self.bridge.getLastDiscoveredDevice()
        if device:
            try:
                name = device.objectForKey_(objc_str("name")).UTF8String()
                uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
                rssi = device.objectForKey_(objc_str("rssi")).intValue()
                major = device.objectForKey_(objc_str("major")).intValue()
                minor = device.objectForKey_(objc_str("minor")).intValue()

                # เก็บ UUID ล่าสุด
                self.current_device_uuid = uuid
                
                # อัพเดทตัวแปรสำหรับ update_ui
                self._uuid = uuid
                self._major = major
                self._minor = minor

                # ใช้ update_ui method ใหม่ (รวม RSSI)
                self.update_ui(name, rssi)
                
            except Exception as e:
                Logger.error(f"Error processing device data: {e}")

    def test_rssi_features(self):
        """ทดสอบ RSSI features ใหม่"""
        Logger.info("BluetoothApp: Testing RSSI features...")
        
        try:
            if self.current_device_uuid:
                # Test RSSI monitoring
                self.start_rssi_monitoring(None)
                
                # Test device info retrieval
                Clock.schedule_once(lambda dt: self.get_device_info(None), 2.0)
                
                Logger.info("✅ RSSI features test initiated")
                return True
            else:
                Logger.info("❌ No device available for RSSI testing")
                return False
                
        except Exception as e:
            Logger.error(f"❌ RSSI features test failed: {e}")
            return False

    def on_stop(self):
        """หยุดการทำงานเมื่อปิด app"""
        Logger.info("BluetoothApp: Stopping...")
        self.bridge.stopBluetoothScan()
    
    def reconnect(self):
        """เก็บ method เดิมไว้เพื่อ compatibility"""
        Logger.info(f"Device: {self.title} try to reconnect ...")
        if hasattr(self, '_device'):
            self.connect_gatt(self._device)
        elif self.current_device_uuid:
            self.reconnect_device(None)


if __name__ == '__main__':
    app = BluetoothScanApp()
    
    # ทดสอบ RSSI features หลังจากเริ่ม app
    def test_after_start():
        Clock.schedule_once(lambda dt: app.test_rssi_features(), 5.0)
    
    test_after_start()
    app.run()
