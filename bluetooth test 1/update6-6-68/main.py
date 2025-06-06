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

    def build(self):
        # สร้าง layout หลัก
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Label สำหรับแสดงข้อมูล device
        self.label = Label(text="Initializing Bluetooth...", size_hint_y=0.7)
        
        # สร้าง buttons layout
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3, spacing=10)
        
        # ปุ่มต่างๆ
        scan_btn = Button(text="Start Scan")
        scan_btn.bind(on_press=self.start_scan)
        
        stop_btn = Button(text="Stop Scan")
        stop_btn.bind(on_press=self.stop_scan)
        
        connect_btn = Button(text="Connect")
        connect_btn.bind(on_press=self.connect_device)
        
        reconnect_btn = Button(text="Reconnect")
        reconnect_btn.bind(on_press=self.reconnect_device)
        
        config_btn = Button(text="Config Auto")
        config_btn.bind(on_press=self.configure_auto_reconnect)
        
        # เพิ่ม buttons ใน layout
        button_layout.add_widget(scan_btn)
        button_layout.add_widget(stop_btn)
        button_layout.add_widget(connect_btn)
        button_layout.add_widget(reconnect_btn)
        button_layout.add_widget(config_btn)
        
        # เพิ่มใน main layout
        main_layout.add_widget(self.label)
        main_layout.add_widget(button_layout)
        
        # สร้าง bridge และเริ่มต้น
        self.bridge = BluetoothBridge.alloc().init()
        self.current_device_uuid = None
        
        # เริ่ม scan อัตโนมัติ
        self.start_scan(None)
        
        Clock.schedule_interval(self.check_discovered_device, 1.0)
        return main_layout

    def start_scan(self, instance):
        """เริ่ม scan หา devices"""
        Logger.info("BluetoothApp: Starting scan...")
        self.bridge.startBluetoothScan()
        self.update_label("Scanning for devices...")

    def stop_scan(self, instance):
        """หยุด scan"""
        Logger.info("BluetoothApp: Stopping scan...")
        self.bridge.stopBluetoothScan()
        self.update_label("Scan stopped")

    def connect_device(self, instance):
        """เชื่อมต่อกับ device ล่าสุดที่เจอ"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothApp: Connecting to device: {self.current_device_uuid}")
            self.bridge.connectToDeviceWithUUID_(self.current_device_uuid)
            self.update_label(f"Connecting to device...\nUUID: {self.current_device_uuid}")
        else:
            self.update_label("No device found to connect")

    def reconnect_device(self, instance):
        """ทดสอบ reconnect method ใหม่"""
        if self.current_device_uuid:
            Logger.info(f"BluetoothApp: Testing reconnect to device: {self.current_device_uuid}")
            self.bridge.reconnectToDeviceWithUUID_(self.current_device_uuid)
            self.update_label(f"Testing reconnect...\nUUID: {self.current_device_uuid}")
        else:
            self.update_label("No device found to reconnect")

    def configure_auto_reconnect(self, instance):
        """ทดสอบ configuration methods"""
        Logger.info("BluetoothApp: Configuring auto reconnect...")
        
        # เปิดใช้งาน auto reconnect
        self.bridge.setAutoReconnectEnabled_(True)
        
        # ตั้งค่า max attempts
        self.bridge.setMaxReconnectAttempts_(5)
        
        # ดึงข้อมูลสถานะ
        connected_count = self.bridge.getConnectedDevicesCount()
        is_scanning = self.bridge.isScanning()
        
        status_text = f"Auto Reconnect: Enabled\nMax Attempts: 5\nConnected Devices: {connected_count}\nIs Scanning: {is_scanning}"
        self.update_label(status_text)
        
        Logger.info("BluetoothApp: Auto reconnect configured")

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

            # แสดงข้อมูล device
            display_text = f"Device: {name}\nUUID: {uuid}\nRSSI: {rssi}\nMajor: {major} Minor: {minor}"
            
            # เพิ่มข้อมูลสถานะ
            connected_count = self.bridge.getConnectedDevicesCount()
            is_scanning = self.bridge.isScanning()
            
            display_text += f"\n\nConnected: {connected_count}\nScanning: {is_scanning}"
            
            print(display_text)
            self.label.text = display_text

    def test_all_methods(self):
        """ทดสอบ methods ทั้งหมด"""
        Logger.info("BluetoothApp: Testing all new methods...")
        
        try:
            # Test 1: Configuration
            self.bridge.setAutoReconnectEnabled_(True)
            self.bridge.setMaxReconnectAttempts_(3)
            Logger.info("✅ Configuration methods work")
            
            # Test 2: Status methods
            is_scanning = self.bridge.isScanning()
            connected_count = self.bridge.getConnectedDevicesCount()
            Logger.info(f"✅ Status methods work - Scanning: {is_scanning}, Connected: {connected_count}")
            
            # Test 3: Device info methods
            all_devices = self.bridge.getAllDiscoveredDevices()
            connected_devices = self.bridge.getConnectedDevices()
            Logger.info(f"✅ Device info methods work - Discovered: {len(all_devices)}, Connected: {len(connected_devices)}")
            
            # Test 4: Reconnect (if device available)
            if self.current_device_uuid:
                self.bridge.reconnectToDeviceWithUUID_(self.current_device_uuid)
                Logger.info("✅ Reconnect method called")
            
            return True
            
        except Exception as e:
            Logger.error(f"❌ Method test failed: {e}")
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
    
    # ทดสอบ methods ก่อนเริ่ม app
    def test_after_start():
        Clock.schedule_once(lambda dt: app.test_all_methods(), 3.0)
    
    test_after_start()
    app.run()
