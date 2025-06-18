from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE

import kivy
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.metrics import dp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

import time

load_framework(INCLUDE.Foundation)

BluetoothBridge = autoclass('BluetoothBridge')
NSDictionary = autoclass('NSDictionary')
NSData = autoclass('NSData')

KV = '''
<DeviceListItem@OneLineListItem>:
    device_uuid: ""
    device_name: ""
    device_rssi: 0
    
    text: f"{self.device_name} (RSSI: {self.device_rssi})"
    on_release: app.on_device_selected(self.device_uuid, self.device_name)

MDBoxLayout:
    orientation: "vertical"

    MDTopAppBar:
        title: "Bluetooth Scanner"
        right_action_items: [["theme-light-dark", lambda x: app.switch_theme_style()], ["exit-to-app", lambda x: app.close_application()]]

    MDBottomNavigation:

        MDBottomNavigationItem:
            name: 'scanner'
            text: 'Scanner'
            icon: 'bluetooth'

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(10)
                padding: dp(20)

                MDLabel:
                    text: "Bluetooth Device Scanner"
                    size_hint_y: None
                    height: dp(40)
                    halign: "center"
                    bold: True
                    font_style: "H5"

                MDCard:
                    size_hint_y: None
                    height: dp(250)
                    md_bg_color: 1, 0.8, 0.6, 1
                    
                    AnchorLayout:
                        anchor_x: "center"
                        anchor_y: "center"
                        
                        MDLabel:
                            id: scan_status
                            text: "Press 'Start Scan' to discover devices"
                            font_size: "12sp"
                            size: self.texture_size
                            halign: "center"
                        ScrollView:
                            size_hint: 1, 1
                            do_scroll_x: False
                            do_scroll_y: True
                            bar_width: dp(4)
                            MDList:
                                id: device_list
                                size_hint_y: None
                                height: self.minimum_height
                MDRaisedButton:
                    text: "Start Scan"
                    
                    on_press: app.start_scan(self)
                    


                MDRaisedButton:
                    text: "Stop Scan"
                    on_press: app.stop_bluetooth_scan()

                MDRaisedButton:
                    text: "Clear List"
                    on_press: app.clear_device_list()

        MDBottomNavigationItem:
            name: 'connection'
            text: 'Connection'
            icon: 'bluetooth-connect'

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(20)
                padding: dp(20)

                MDLabel:
                    text: "Device Connection"
                    size_hint_y: None
                    height: dp(40)
                    halign: "center"
                    bold: True
                    font_style: "H5"

                MDCard:
                    size_hint_y: None
                    height: dp(200)
                    md_bg_color: app.theme_cls.primary_light

                    MDLabel:
                        id: connection_status
                        text: "No device selected"
                        halign: "center"
                        valign: "center"

                MDBoxLayout:
                    orientation: "horizontal"
                    spacing: dp(10)
                    size_hint_y: None
                    height: dp(50)

                    MDRaisedButton:
                        text: "Connect GATT"
                        on_press: app.connect_to_selected_device()

                    MDRaisedButton:
                        text: "Disconnect"
                        on_press: app.disconnect_from_device()

        MDBottomNavigationItem:
            name: 'info'
            text: 'Info'
            icon: 'information'

            MDCard:
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.8, 0.6
                pos_hint: {"center_x": .5, "center_y": .5}

                MDLabel:
                    text: "Bluetooth GATT Scanner\\n\\nFeatures:\\n• Unique device detection\\n• Click device to connect\\n• Real-time RSSI monitoring"
                    halign: "center"
                    valign: "center"
'''



class BluetoothGATTApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ✅ Data attributes - ไม่เกี่ยวกับ UI
        self.bridge = None
        self.discovered_devices = {}  # UUID เป็น key
        self.selected_device_uuid = None
        self.current_device_uuid = None
        self.selected_device_name = None
        self.is_scanning = False
        self.label = None
        self.is_connected = False
        
        # ✅ UI references - เก็บ reference ไว้
        self.scan_status_label = None
        self.connection_status_label = None
        self.device_list_widget = None
        
    def build(self):
        """สร้าง UI และเชื่อม references"""
        root = Builder.load_string(KV)
        
        # ✅ เชื่อม UI references
        self.scan_status_label = root.ids.scan_status
        self.connection_status_label = root.ids.connection_status
        self.device_list_widget = root.ids.device_list
        
        # ✅ Initialize Bluetooth
        self.initialize_bluetooth()
        
        return root
    
    def initialize_bluetooth(self):
        """เริ่มต้น Bluetooth bridge"""
        try:
            self.bridge = BluetoothBridge.alloc().init()
            Logger.info("✅ BluetoothBridge initialized successfully")
            self.update_scan_status("✅ Bluetooth ready - Press 'Start Scan'")
        except Exception as e:
            Logger.error(f"❌ Failed to initialize BluetoothBridge: {e}")
            self.update_scan_status("❌ Bluetooth initialization failed")

    # ✅ ========== BLUETOOTH LOGIC METHODS ==========
    
    def start_bluetooth_scan(self, instance=None):
        """เริ่มการ scan อุปกรณ์"""
        if not self.bridge:
            self.update_scan_status("❌ Bluetooth not initialized")
            return
            
        Logger.info("🔍 Starting Bluetooth scan...")
        
        try:
            # ล้างข้อมูลเก่า
            self.clear_discovered_devices()
            
            # เริ่ม scan ใน Swift
            self.bridge.performFullDeviceScan()
            self.is_scanning = True
            
            # อัพเดท UI
            self.update_scan_status("🔍 Scanning for devices...")
            
            # เริ่ม polling สำหรับ devices ใหม่
            Clock.schedule_interval(self.poll_discovered_devices, 1.5)
            
        except Exception as e:
            Logger.error(f"❌ Error starting scan: {e}")
            self.update_scan_status(f"❌ Scan error: {e}")

    def stop_bluetooth_scan(self):
        """หยุดการ scan"""
        if not self.bridge:
            return
            
        try:
            self.bridge.stopBluetoothScan()
            self.is_scanning = False
            
            # หยุด polling
            Clock.unschedule(self.poll_discovered_devices)
            
            device_count = len(self.discovered_devices)
            self.update_scan_status(f"🛑 Scan stopped - Found {device_count} unique devices")
            
            Logger.info(f"🛑 Bluetooth scan stopped, found {device_count} devices")
            
        except Exception as e:
            Logger.error(f"❌ Error stopping scan: {e}")

    def poll_discovered_devices(self, dt):
        """ตรวจสอบ devices ใหม่จาก Swift"""
        if not self.bridge or not self.is_scanning:
            return False
            
        try:
            # ✅ ดึงข้อมูลจาก Swift
            devices_array = self.bridge.getUniqueDevices()
            current_count = self.bridge.getUniqueDevicesCount()
            
            # ✅ เช็คว่ามี device ใหม่หรือไม่
            if current_count > len(self.discovered_devices):
                self.process_new_devices(devices_array)
                self.update_scan_status(f"🔍 Scanning... Found {current_count} unique devices")
            
        except Exception as e:
            Logger.error(f"❌ Error polling devices: {e}")
        
        return True  # Continue polling

    def process_new_devices(self, devices_array):
        """ประมวลผล devices ใหม่ที่ได้จาก Swift"""
        try:
            for i in range(devices_array.count()):
                device_dict = devices_array.objectAtIndex_(i)
                
                # ✅ แปลงข้อมูลจาก NSDictionary เป็น Python dict
                device_data = self.convert_nsdict_to_python(device_dict)
                
                # ✅ เช็คว่าเป็น device ใหม่หรือไม่
                device_uuid = device_data.get('uuid')
                if device_uuid and device_uuid not in self.discovered_devices:
                    # เพิ่ม device ใหม่
                    self.add_new_device(device_data)
                    
        except Exception as e:
            Logger.error(f"❌ Error processing new devices: {e}")

    def convert_nsdict_to_python(self, ns_dict):
        """แปลง NSDictionary เป็น Python dict"""
        try:
            name = ns_dict.objectForKey_(objc_str("name"))
            uuid = ns_dict.objectForKey_(objc_str("uuid"))
            rssi = ns_dict.objectForKey_(objc_str("rssi"))
            major = ns_dict.objectForKey_(objc_str("major"))
            minor = ns_dict.objectForKey_(objc_str("minor"))
            timestamp = ns_dict.objectForKey_(objc_str("timestamp"))

            return {
                "name": name.UTF8String() if name else "Unknown Device",
                "uuid": uuid.UTF8String() if uuid else None,
                "rssi": rssi.intValue() if rssi else -999,
                "major": major.intValue() if major else 0,
                "minor": minor.intValue() if minor else 0,
                "timestamp": timestamp.doubleValue() if timestamp else 0
            }
        except Exception as e:
            Logger.error(f"❌ Error converting NSDictionary: {e}")
            return {}

    def add_new_device(self, device_data):
        """เพิ่ม device ใหม่เข้าระบบ"""
        device_uuid = device_data.get('uuid')
        if not device_uuid:
            return
            
        # ✅ เพิ่มเข้า Python dict
        self.discovered_devices[device_uuid] = device_data
        
        # ✅ เพิ่มเข้า UI
        self.add_device_to_ui(device_data)
        
        Logger.info(f"📱 Added new device: {device_data['name']} ({device_uuid[:8]}...)")

    def clear_discovered_devices(self):
        """ล้างข้อมูล devices ทั้งหมด"""
        # ล้าง Python data
        self.discovered_devices.clear()
        
        # ล้าง Swift data
        if self.bridge:
            self.bridge.clearUniqueDevices()
        
        # ล้าง UI
        self.clear_device_list_ui()
        
        Logger.info("🗑️ All devices cleared")

    def connect_to_selected_device(self):
        """เชื่อมต่อกับ device ที่เลือก"""
        if not self.selected_device_uuid or not self.bridge:
            self.update_connection_status("❌ No device selected")
            return
            
        Logger.info(f"🔄 Connecting to: {self.selected_device_name}")
        
        try:
            # เชื่อมต่อผ่าน Swift
            success = self.bridge.connectToDeviceWithUUID_(objc_str(self.selected_device_uuid))
            
            if success:
                self.update_connection_status(f"🔄 Connecting to {self.selected_device_name}...")
                # ตรวจสอบสถานะหลัง 3 วินาที
                Clock.schedule_once(self.check_connection_result, 3.0)
            else:
                self.update_connection_status("❌ Failed to initiate connection")
                
        except Exception as e:
            Logger.error(f"❌ Connection error: {e}")
            self.update_connection_status(f"❌ Connection error: {e}")

    def check_connection_result(self, dt):
        """ตรวจสอบผลการเชื่อมต่อ"""
        if not self.selected_device_uuid or not self.bridge:
            return
            
        try:
            is_connected = self.bridge.isDeviceConnected_(objc_str(self.selected_device_uuid))
            connection_state = self.bridge.getConnectionStateForDevice_(objc_str(self.selected_device_uuid))
            
            if is_connected:
                self.is_connected = True
                connection_info = f"✅ Connected to {self.selected_device_name}\n"
                connection_info += f"UUID: {self.selected_device_uuid[:8]}...\n"
                connection_info += f"State: {connection_state}"
                self.update_connection_status(connection_info)
                
                Logger.info(f"✅ Successfully connected to {self.selected_device_name}")
            else:
                self.update_connection_status(f"❌ Connection failed\nState: {connection_state}")
                Logger.warning(f"❌ Connection failed: {connection_state}")
                
        except Exception as e:
            Logger.error(f"❌ Error checking connection: {e}")
            self.update_connection_status(f"❌ Connection check failed")

    def disconnect_from_device(self):
        """ตัดการเชื่อมต่อจาก device"""
        if not self.selected_device_uuid or not self.bridge:
            self.update_connection_status("❌ No device to disconnect")
            return
            
        try:
            self.bridge.disconnectPeripheralWith_(objc_str(self.selected_device_uuid))
            self.is_connected = False
            
            self.update_connection_status(f"🔌 Disconnected from {self.selected_device_name}")
            Logger.info(f"🔌 Disconnected from {self.selected_device_name}")
            
        except Exception as e:
            Logger.error(f"❌ Disconnect error: {e}")
            self.update_connection_status(f"❌ Disconnect error")

    def check_disconnection_result(self, dt):
        """ตรวจสอบผลการตัดการเชื่อมต่อ"""
        if not self.selected_device_uuid or not self.bridge:
            return
            
        try:
            is_connected = self.bridge.isDeviceConnected_(objc_str(self.selected_device_uuid))
            
            if not is_connected:
                self.is_connected = False
                connection_info = f"✅ Disconnected from {self.selected_device_name}\n"
                connection_info += f"UUID: {self.selected_device_uuid[:8]}..."
                self.update_connection_status(connection_info)
                
                Logger.info(f"✅ Successfully disconnected from {self.selected_device_name}")
            else:
                self.update_connection_status("❌ Disconnection failed")
                
        except Exception as e:
            Logger.error(f"❌ Error checking disconnection: {e}")
            self.update_connection_status(f"❌ Error checking disconnection: {e}")

    # ✅ ========== UI UPDATE METHODS ==========
    
    @mainthread
    def update_scan_status(self, message):
        """อัพเดท scan status ใน UI"""
        if self.scan_status_label:
            self.scan_status_label.text = message
        Logger.info(f"Scan Status: {message}")

    @mainthread
    def update_connection_status(self, message):
        """อัพเดท connection status ใน UI"""
        if self.connection_status_label:
            self.connection_status_label.text = message
        Logger.info(f"Connection Status: {message}")

    @mainthread
    def add_device_to_ui(self, device_data):
        """เพิ่ม device เข้า UI list"""
        if not self.device_list_widget:
            return
            
        try:
            # สร้าง list item
            device_text = f"📱 {device_data['name']}\n🆔 {device_data['uuid'][:8]}... | 📶 {device_data['rssi']} dBm"
            
            device_item = OneLineListItem(
                text=device_text,
                on_release=lambda x: self.on_device_selected(device_data['uuid'], device_data['name'])
            )
            
            # เพิ่มเข้า list
            self.device_list_widget.add_widget(device_item)
            
        except Exception as e:
            Logger.error(f"❌ Error adding device to UI: {e}")

    @mainthread
    def clear_device_list_ui(self):
        """ล้าง device list ใน UI"""
        if self.device_list_widget:
            self.device_list_widget.clear_widgets()

    def clear_device_list(self):
        """ล้างรายการ devices (เรียกจาก UI)"""
        self.clear_discovered_devices()
        self.update_scan_status("🗑️ Device list cleared")

    # ✅ ========== EVENT HANDLERS ==========
    
    def on_device_selected(self, device_uuid, device_name):
        """จัดการเมื่อผู้ใช้เลือก device"""
        Logger.info(f"📱 Device selected: {device_name} ({device_uuid})")
        
        # เก็บข้อมูล device ที่เลือก
        self.selected_device_uuid = device_uuid
        self.selected_device_name = device_name
        
        # แสดง dialog ยืนยัน
        self.show_connection_dialog(device_name, device_uuid)

    def show_connection_dialog(self, device_name, device_uuid):
        """แสดง dialog ยืนยันการเชื่อมต่อ"""
        dialog_text = f"Connect to device?\n\n"
        dialog_text += f"Name: {device_name}\n"
        dialog_text += f"UUID: {device_uuid[:8]}...\n"
        
        # ดึงข้อมูลเพิ่มเติมจาก discovered_devices
        device_data = self.discovered_devices.get(device_uuid)
        if device_data:
            dialog_text += f"RSSI: {device_data['rssi']} dBm\n"
            dialog_text += f"Major: {device_data['major']} | Minor: {device_data['minor']}"

        dialog = MDDialog(
            title="Connect to Device",
            text=dialog_text,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="CONNECT",
                    on_release=lambda x: self.confirm_connection(dialog)
                ),
            ],
        )
        dialog.open()

    def confirm_connection(self, dialog):
        """ยืนยันการเชื่อมต่อ"""
        dialog.dismiss()
        
        # อัพเดท connection status
        connection_info = f"📱 Selected: {self.selected_device_name}\n"
        connection_info += f"🆔 UUID: {self.selected_device_uuid[:8]}...\n"
        connection_info += f"📶 Ready to connect"
        
        self.update_connection_status(connection_info)
        
        # เชื่อมต่อทันที
        self.connect_to_selected_device()

    # ✅ ========== UTILITY METHODS ==========
    
    def get_device_by_uuid(self, uuid):
        """ดึงข้อมูล device จาก UUID"""
        return self.discovered_devices.get(uuid)

    def get_discovered_device_count(self):
        """ดึงจำนวน devices ที่เจอ"""
        return len(self.discovered_devices)

    def get_all_discovered_devices(self):
        """ดึงรายการ devices ทั้งหมด"""
        return list(self.discovered_devices.values())

    def is_device_discovered(self, uuid):
        """ตรวจสอบว่า device ถูกค้นพบแล้วหรือไม่"""
        return uuid in self.discovered_devices

    def get_connection_info(self):
        """ดึงข้อมูลการเชื่อมต่อปัจจุบัน"""
        if not self.selected_device_uuid:
            return {"status": "no_device_selected"}
            
        return {
            "uuid": self.selected_device_uuid,
            "name": self.selected_device_name,
            "is_connected": self.is_connected,
            "device_data": self.get_device_by_uuid(self.selected_device_uuid)
        }

    # ✅ ========== APP LIFECYCLE METHODS ==========
    
    def switch_theme_style(self):
        """สลับธีม"""
        self.theme_cls.theme_style = "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        Logger.info(f"Theme switched to: {self.theme_cls.theme_style}")

    def close_application(self):
        """ปิดแอปพลิเคชัน"""
        Logger.info("🔴 Application closing...")
        self.stop()

    def on_stop(self):
        """จัดการเมื่อแอปหยุดทำงาน"""
        Logger.info("🔴 BluetoothGATTApp stopping...")
        
        try:
            # หยุด scan ถ้ายังทำงานอยู่
            if self.is_scanning:
                self.stop_bluetooth_scan()
            
            # ตัดการเชื่อมต่อถ้ายังเชื่อมต่ออยู่
            if self.is_connected:
                self.disconnect_from_device()
            
            # หยุด Clock schedules
            Clock.unschedule(self.poll_discovered_devices)
            Clock.unschedule(self.check_connection_result)
            
            Logger.info("✅ BluetoothGATTApp stopped cleanly")
            
        except Exception as e:
            Logger.error(f"❌ Error during app shutdown: {e}")

    # ✅ ========== DEBUG METHODS ==========
    
    def print_discovered_devices(self):
        """พิมพ์รายการ devices ที่เจอ (สำหรับ debug)"""
        Logger.info(f"📱 Discovered Devices ({len(self.discovered_devices)}):")
        for uuid, device in self.discovered_devices.items():
            Logger.info(f"  - {device['name']} | {uuid[:8]}... | {device['rssi']} dBm")

    def get_app_status(self):
        """ดึงสถานะแอปทั้งหมด (สำหรับ debug)"""
        return {
            "bluetooth_initialized": self.bridge is not None,
            "is_scanning": self.is_scanning,
            "discovered_count": len(self.discovered_devices),
            "selected_device": self.selected_device_name,
            "is_connected": self.is_connected,
            "ui_references": {
                "scan_status": self.scan_status_label is not None,
                "connection_status": self.connection_status_label is not None,
                "device_list": self.device_list_widget is not None
            }
        }

    def start_scan(self, instance):
        """เริ่ม scan หา devices"""
        Logger.info("BluetoothGATTApp: Starting full device scan...")
        
        # ใช้ method ใหม่ที่มี cleanup
        self.bridge.performFullDeviceScan()
        self.update_label("Scanning for devices...")
        Clock.schedule_interval(self.check_discovered_device, 1.0)
    
        
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
        self.root.ids.scan_status.text = text

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
        # สร้าง/อัพเดท discovered devices list (ป้องกันซ้ำ)
        if not hasattr(self, 'discovered_devices_list'):
            self.discovered_devices_list = {}
        
        # เพิ่มหรืออัพเดทอุปกรณ์ในรายการ
        self.discovered_devices_list[uuid] = {
            'name': name,
            'uuid': uuid,
            'rssi': rssi
        }
        
        # สร้าง display text เป็น list ตัวเลือก (จำกัดความยาว)
        display_text = "📱 Devices:\n"
        display_text += "━━━━━━━━━━━━━━━━━━━━\n"
        
        # จำกัดการแสดงผลไม่เกิน 4 devices เพื่อไม่ให้ล้นกล่อง
        device_items = list(self.discovered_devices_list.items())
        max_display = 4  # จำกัดแสดงแค่ 4 devices
        
        for i, (device_uuid, device_info) in enumerate(device_items[-max_display:], 1):
            display_text += f"[{i}] {device_info['name'][:12]}...\n"  # จำกัดชื่อ 12 ตัวอักษร
            display_text += f"UUID: {device_info['uuid'][:8]}...\n"
            display_text += f"RSSI: {device_info['rssi']} dBm\n"
            display_text += "━━━━━━━━━━━━━━━━━━━━\n"
        
        # แสดงจำนวนทั้งหมด
        if len(self.discovered_devices_list) > max_display:
            display_text += f"...และอีก {len(self.discovered_devices_list) - max_display} devices\n"
        
        display_text += f"Total: {len(self.discovered_devices_list)}"
        
        # เพิ่มข้อมูลสถานะ GATT
        if hasattr(self, 'gatt_connected') and self.gatt_connected:
            connection_state = self.bridge.getConnectionStateForDevice_(objc_str(uuid))
            display_text += f"\nGATT: {connection_state}"
        else:
            display_text += f"\nGATT: Not Connected"
        
        # เพิ่มข้อมูลสถานะระบบ
        connected_count = self.bridge.getConnectedDevicesCount()
        
        self.update_scan_status(display_text)
    
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
            # ✅ Force ให้ Swift อ่าน RSSI ใหม่
            self.bridge.startRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            # รอให้ Swift อ่านค่าใหม่
            Clock.schedule_once(self.display_updated_rssi, 0.5)
            
            return True
            
        except Exception as e:
            Logger.error(f"Error in real-time RSSI update: {e}")
            return True

    def display_updated_rssi(self, dt):
        """แสดงค่า RSSI ที่อัพเดทแล้ว"""
        try:
            # ✅ ดึงค่า RSSI ปัจจุบันจาก Swift
            current_rssi = self.bridge.getCurrentRSSIForDevice_(objc_str(self.current_device_uuid))
            
            # ดึงข้อมูลอื่นๆ
            current_device = self.bridge.getCurrentDeviceInfo()
            
            if current_device and current_rssi != -999:
                name = current_device.objectForKey_(objc_str("name"))
                uuid = current_device.objectForKey_(objc_str("uuid"))
                major = current_device.objectForKey_(objc_str("major"))
                minor = current_device.objectForKey_(objc_str("minor"))
                
                rssi_value = current_rssi  # ใช้ค่าที่ได้จาก getCurrentRSSI
                
                # เพิ่มตัวนับ
                self.rssi_update_count += 1
                
                # ✅ Debug: แสดงค่าเปรียบเทียบ
                old_rssi = getattr(self, 'last_rssi', None)
                Logger.info(f"🔍 Debug - Old RSSI: {old_rssi}, New RSSI: {rssi_value}")
                
                # ตรวจสอบการเปลี่ยนแปลง
                if old_rssi is None or old_rssi != rssi_value:
                    Logger.info(f"📶 RSSI Changed: {old_rssi} → {rssi_value} dBm")
                    self.last_rssi = rssi_value
                    change_indicator = "🔄 CHANGED"
                else:
                    Logger.info(f"📶 RSSI Same: {rssi_value} dBm")
                    change_indicator = "➡️ SAME"
                
                
                # แสดงผล
                current_time = time.strftime("%H:%M:%S")
                
                rssi_display = f"📶 RSSI Monitor (LIVE)\n"
                rssi_display += f"━━━━━━━━━━━━━━━━━━━━\n"
                rssi_display += f"🕐 Time: {current_time}\n"
                rssi_display += f"📱 Device: {name.UTF8String() if name else 'Unknown'}\n"
                rssi_display += f"🆔 UUID: {uuid.UTF8String()[:8] if uuid else 'N/A'}...\n"
                rssi_display += f"📶 RSSI: {rssi_value} dBm {change_indicator}\n"
                rssi_display += f"🔢 Major: {major.intValue() if major else 0} | Minor: {minor.intValue() if minor else 0}\n"
                rssi_display += f"━━━━━━━━━━━━━━━━━━━━\n"
                rssi_display += f"🔄 Updates: {self.rssi_update_count}\n"
                rssi_display += f"📈 Last Change: {old_rssi} → {rssi_value}\n"
                rssi_display += f"⏱️ Refreshing every 1s\n"
                rssi_display += f"🛑 Tap RSSI again to stop"
                
                self.update_label(rssi_display)
                
            else:
                Logger.warning(f"No valid RSSI value received: {current_rssi}")
            
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
