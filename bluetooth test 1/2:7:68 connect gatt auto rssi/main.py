from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
from kivy.logger import Logger
import time

from kivymd.app import MDApp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
import requests
import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Ellipse, Rectangle, Line, Translate
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from datetime import datetime



load_framework(INCLUDE.Foundation)

BluetoothBridge = autoclass('BluetoothBridge')
NSDictionary = autoclass('NSDictionary')
NSData = autoclass('NSData')

KV = '''
MDBoxLayout:
    orientation: "vertical"  
    MDTopAppBar:
        title: "Bluetooth Application"
        right_action_items: [["theme-light-dark", lambda x: app.switch_theme_style()], ["exit-to-app", lambda x: app.close_application()]]
    MDBottomNavigation:

        MDBottomNavigationItem:
            name: 'screen 1'
            text: 'Scanner'
            icon: 'bluetooth'

            MDLabel
                id: Ble
                text: "Bluetooth Scanner"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_style: "H4"
                pos_hint: {"center_x": .5, "center_y": .85}

            MDLabel
                id: status
                halign: "center"
                size_hint_y: None
                pos_hint: {"center_x": .5, "center_y": .15}
            
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.7, 0.3
                pos_hint: {"center_x": .5, "center_y": .6}
                MDLabel
                    id: label
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .5, "center_y": .5}

            MDRectangleFlatButton:
                text: "Start"
                text_color: "black"
                on_press: app.start_scan(self)
                md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .25, "center_y": .35}

            MDRectangleFlatButton:
                text: "Stop"
                text_color: "black"
                on_press: app.stop_service()
                md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .75, "center_y": .35}
                
            MDRectangleFlatButton:
                text: "Send"
                text_color: "black"
                on_press: app.send_data()
                md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .5, "center_y": .35}

        MDBottomNavigationItem:
            name: 'screen 2'
            text: 'Position'
            icon: 'map-marker-account'

            MDLabel
                id: Ble
                text: "Position Calculation"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_style: "H4"
                pos_hint: {"center_x": .5, "center_y": .85}

            MDLabel
                id: status2
                halign: "center"
                font_size: "12sp" 
                size_hint_y: None
                pos_hint: {"center_x": .5, "center_y": .58}
            
            MDLabel
                id: Goto
                text: "You Want to Go to point"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_size: "16sp" 
                pos_hint: {"center_x": .5, "center_y": .74}
            
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.3, 0.1
                pos_hint: {"center_x": .65, "center_y": .66}
                MDLabel
                    id: label_point
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .65, "center_y": .66}
                    
            # Dropdown Menu
            MDRaisedButton:
                id: menu_button_cal
                text: "Point"
                on_release: app.open_menu_cal(self)
                pos_hint: {"center_x": .35, "center_y": .66}

            MDRectangleFlatButton:
                text: "Start"
                text_color: "black"
                on_press: app.start_service()
                md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .40, "center_y": .51}

            MDRectangleFlatButton:
                text: "Stop"
                text_color: "black"
                on_press: app.stop_service()
                md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .60, "center_y": .51}
                
            MDLabel
                id: Point
                text: "RSSI Calculate"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_size: "16sp" 
                pos_hint: {"center_x": .3, "center_y": .43}
                
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.3, 0.1
                pos_hint: {"center_x": .3, "center_y": .36}
                MDLabel
                    id: label_rssi_cal
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .3, "center_y": .36}
                    
            MDLabel
                id: Point
                text: "AoA/RSSI Calculated"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_size: "16sp" 
                pos_hint: {"center_x": .7, "center_y": .43}
                
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.3, 0.1
                pos_hint: {"center_x": .7, "center_y": .36}
                MDLabel
                    id: label_aoa_cal
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .7, "center_y": .36}
                    
            MDLabel
                id: Status
                text: "Status (Error ≤ 5 meters)"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_size: "16sp" 
                pos_hint: {"center_x": .5, "center_y": .25}
                
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.3, 0.1
                pos_hint: {"center_x": .3, "center_y": .17}
                MDLabel
                    id: label_rssi_status
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .3, "center_y": .50}
                    # text: root.ids.success_input.text  # ดึงค่าจาก TextField
                    
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.3, 0.1
                pos_hint: {"center_x": .7, "center_y": .17}
                MDLabel
                    id: label_aoa_status
                    theme_text_color: "Custom"
                    size_hint: 0.3, 0.1
                    halign: "center"
                    pos_hint: {"center_x": .7, "center_y": .50}
                    # text: root.ids.success_input.text  # ดึงค่าจาก TextField
            
            MDRaisedButton:
                text: "Edit Status"
                text_color: "black"
                on_press: app.toggle_edit_status(self)  # เรียกฟังก์ชัน toggle_edit_status
                # md_bg_color: app.theme_cls.primary_light
                pos_hint: {"center_x": .37, "center_y": .07}
                
            MDRaisedButton:
                text: "OK"
                text_color: "black"
                on_press: app.send_data()
                pos_hint: {"center_x": .62, "center_y": .07}




'''
class MapScreen(Screen):
    pass

class DemoPage(Screen):
    pass

sm = ScreenManager()
sm.add_widget(DemoPage(name='demopage'))
class ScannerDispatcher:
    def __init__(self):
        self.bluetooth_bridge = BluetoothBridge.alloc().init()
        self.bluetooth_bridge.setDelegate_(self)
        self.bluetooth_bridge.startScan()
        self.connected_gatt_uuids = set()

class BluetoothGATTApp(MDApp):

    def build(self):
        # สร้าง layout หลัก
        self.screen = Builder.load_string(KV)
        self.previous_point = None
        self.request_ios_permissions()
        self.status_aoa = "ready"      # แทนที่จะเป็น None
        self.status_rssi = "ready"     # แทนที่จะเป็น None   # สถานะการคำนวณ RSSI
        self.dialog = None
        self.scanned_point = None
        self.scanned_devices = []
        self.bridge = BluetoothBridge.alloc().init() 
        self.current_device_uuid = None
        self.gatt_connected_devices = set()
        self.seen_target_devices = set()

        
        
        
        # เริ่ม scan อัตโนมัติ
        
        
        Clock.schedule_interval(self.check_discovered_device, 1.0)
    
        self.target_data_set = [
         
           
            {"uuid": "A7E39D7510F2FE254DAE4230DBC6C3A4", "major": 0},
           
            {"uuid": "3D5B8940B5CC24585A5612F6DB393A91", "major": 0},
          
            {"uuid": "D2F287A95EC6EE4FFD170F5EC006DFAE", "major": 0},
          
            {"uuid": "818B88DD1659CE50979E8B0C9257F640", "major": 0}
        ]
        self.found_data = set()  # เก็บข้อมูล beacon ที่พบ
        self.scan_results = []   # เก็บผลลัพธ์การสแกน
        
        self.screen = Builder.load_string(KV)
        self.previous_point = None

    














        #Screen2 Calculation
        self.menu_items_cal = [
            {"viewclass": "OneLineListItem", "text": "A", "on_release": lambda x="A": self.menu_callback_cal(x)},
            {"viewclass": "OneLineListItem", "text": "B", "on_release": lambda x="B": self.menu_callback_cal(x)},
            {"viewclass": "OneLineListItem", "text": "C", "on_release": lambda x="C": self.menu_callback_cal(x)},
            {"viewclass": "OneLineListItem", "text": "D", "on_release": lambda x="D": self.menu_callback_cal(x)},
            {"viewclass": "OneLineListItem", "text": "E", "on_release": lambda x="E": self.menu_callback_cal(x)},
            {"viewclass": "OneLineListItem", "text": "F", "on_release": lambda x="F": self.menu_callback_cal(x)}
        ]
        self.menu_cal = MDDropdownMenu(
            caller=self.screen.ids.menu_button_cal,
            items=self.menu_items_cal,
            width_mult = 0.5,
            position="auto",
        )
        

        #Screen4 Map of table
        self.menu_items_map = [
            {"viewclass": "OneLineListItem", "text": "A", "on_release": lambda x="A": self.menu_callback_map(x)},
            {"viewclass": "OneLineListItem", "text": "B", "on_release": lambda x="B": self.menu_callback_map(x)},
            {"viewclass": "OneLineListItem", "text": "C", "on_release": lambda x="C": self.menu_callback_map(x)},
            {"viewclass": "OneLineListItem", "text": "D", "on_release": lambda x="D": self.menu_callback_map(x)},
            {"viewclass": "OneLineListItem", "text": "E", "on_release": lambda x="E": self.menu_callback_map(x)},
            {"viewclass": "OneLineListItem", "text": "F", "on_release": lambda x="F": self.menu_callback_map(x)},
            # {"viewclass": "OneLineListItem", "text": "All", "on_release": lambda x="All": self.menu_callback_map(x)}
        ]
        self.menu_map = MDDropdownMenu(
            # caller=self.root.ids.menu_button_map,
            items=self.menu_items_map,
            width_mult = 0.5,
            position="auto",
        )

    # เก็บ UUID ที่เคยเจอไว้


    
        return self.screen
    def request_ios_permissions(self):
        """ขอ permission สำหรับ iOS"""
        try:
            from pyobjus import autoclass
            
            # Import iOS classes
            UIApplication = autoclass('UIApplication')
            NSURL = autoclass('NSURL')
            
            # ตรวจสอบ Local Network permission
            self.check_local_network_permission()
            
            Logger.info("iOS permissions requested")
            
        except Exception as e:
            Logger.error(f"Error requesting iOS permissions: {e}")
    
    def check_local_network_permission(self):
        """ตรวจสอบ Local Network permission"""
        try:
            import socket
            
            # สร้าง UDP socket เพื่อ trigger permission dialog
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            # พยายามเชื่อมต่อไป local network
            try:
                sock.connect(('192.168.100.196', 5000))
                Logger.info("✅ Local network permission granted")
                return True
            except socket.error as e:
                Logger.warning(f"Local network permission may be denied: {e}")
                return False
            finally:
                sock.close()
                
        except Exception as e:
            Logger.error(f"Error checking local network permission: {e}")
            return False
    #Screen2 Calculation
    def open_menu_cal(self, caller_cal):
        self.menu_cal.caller = caller_cal
        self.menu_cal.open()
    def reset_menu_caller_cal(self):
        self.menu_cal.caller = self.root.ids.menu_button_cal
    #show point(A,B,C,D,E,F) of Screen 2 (calculation)
    def menu_callback_cal(self, text_item):
        self.menu_cal.dismiss()
        Clock.schedule_once(lambda dt: self.reset_menu_caller_cal(), 0.1)
        print(f"you select point: {text_item}") 
        results_item = '\n'
        results_item += f"\n{text_item}"
        x, y = self.get_coordinates_from_api(text_item)
        if x is not None and y is not None:
            print(f"Coordinates: x = {x}, y = {y}")
            results_item += f"\n({x:.2f}, {y:.2f})\n"
            #keep the x, y and point values ​​of the class.
            self.x_real = x
            self.y_real = y
            self.point = text_item
            
            #check 'point' is change from last time or not?
            if self.previous_point is not None and self.previous_point != self.point:
                self.display_scan_results()
        else:
            print("Point not found in API response")    
        self.root.ids.label_point.text =  results_item
    
    def fetch_data(self, point):
                url = 'http://192.168.100.196:5000/Point' #IP of server to connect database
                try:
                    response = requests.get(url, json={"point": point})  # ส่ง JSON ไปหา API
                    print("Response Text:", response.text)  
                    if response.status_code == 200:
                        data = response.json()
                        print("Data received:", data)
                        Logger.info(f"Data is : {data}")
                        return data
                    else:
                        Logger.error(f"Failed with status code {response.status_code}")
                except Exception as e:
                    Logger.error(f"Error fetching data: {e}")
                return []

    def get_coordinates_from_api(self, point):
        data = self.fetch_data(point)  # send 'point' to API
        if isinstance(data, dict) and data.get("point") == point:
            return data.get("x"), data.get("y")
        return None, None

    def show_alert(self, title, text):
        if not self.dialog:
            self.dialog = MDDialog(
                title=title,
                text=text,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
        else:
            self.dialog.title = title
            self.dialog.text = text

        self.dialog.open()


    def get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def display_scan_results(self):
        self.scanned_devices = []
        scanned_info = ''
        A1_V, A1_H, A2_V, A2_H, A3_V, A3_H, A4_V, A4_H = 0, 0, 0, 0, 0, 0, 0, 0

        for uuid, major, rssi in self.scan_results:
            anchor_id = None
            name = None

            if uuid is None:
                scanned_info = f"[{self.get_timestamp()}] Don't have any Device is Match"
                continue  # ข้ามการประมวลผลตัวนี้

            # กำจัดเครื่องหมาย '-' และทำให้เป็นตัวพิมพ์ใหญ่ (ถ้าจำเป็น)
            uuid = uuid.replace("-", "").upper()

            if uuid == "818B88DD1659CE50979E8B0C9257F640" and major == 0:
                name = "A1(VER)"
                anchor_id = "A1_V"
                A1_V = rssi

            elif uuid == "818B88DD1659CE50979E8B0C9257F640" and major == 111:
                name = "A1(HOR)"
                anchor_id = "A1_H"
                A1_H = rssi
            
            elif uuid == "D2F287A95EC6EE4FFD170F5EC006DFAE" and major == 0:
                name = "A2(VEA)"
                anchor_id = "A2_V"
                A2_V = rssi

            elif uuid == "D2F287A95EC6EE4FFD170F5EC006DFAE" and major == 111:
                name = "A2(VEA)"
                anchor_id = "A2_H"
                A2_H = rssi
            
            elif uuid == "A7E39D7510F2FE254DAE4230DBC6C3A4" and major == 0:
                name = "A3(VEA)"
                anchor_id = "A3_V"
                A3_V = rssi

            elif uuid == "A7E39D7510F2FE254DAE4230DBC6C3A4" and major == 111:
                name = "A3(VEA)"
                anchor_id = "A3_H"
                A3_H = rssi

            elif uuid == "3D5B8940B5CC24585A5612F6DB393A91" and major == 0:
                name = "A4(VEA)"
                anchor_id = "A4_V"
                A4_V = rssi

            elif uuid == "3D5B8940B5CC24585A5612F6DB393A91" and major == 111:
                name = "A4(VEA)"
                anchor_id = "A4_H"
                A4_H = rssi

            else:
                name = "Unknown"
                anchor_id = "Unknown"

            # สร้างข้อความ log พร้อม timestamp
            scanned_info += f"[{self.get_timestamp()}] {name}, RSSI: {rssi} dBm, Major: {major}\n"

            # เก็บข้อมูลเฉพาะ device ที่รู้จักเท่านั้น
            if anchor_id != "Unknown":
                self.scanned_devices.append({
                    "uuid": uuid,
                    "rssi": rssi,
                    "anchor_id": anchor_id
                })

        # แสดงผลลัพธ์ที่เก็บไว้
        print("📋 สรุป scanned_devices ที่จะส่ง:")
        if not self.scanned_devices:
            print(f"[{self.get_timestamp()}] ⚠️ ไม่มี scanned_devices ให้ส่ง")
        else:
            for d in self.scanned_devices:
                print(f"[{self.get_timestamp()}] 🛰️ Anchor: {d['anchor_id']} | RSSI: {d['rssi']} | UUID: {d['uuid']}")

    def send_data(self):
        print(f"[{self.get_timestamp()}] 🔄 เริ่มส่งข้อมูล...")

        # เรียกสแกนและเตรียมข้อมูลก่อนส่ง
        self.display_scan_results()

        if self.x_real is None or self.y_real is None:
            self.show_alert("Please select a Point! Don't have a data to send")
            print(f"[{self.get_timestamp()}] ❌ x_real หรือ y_real ไม่มีค่า")
            return

        elif self.start_scan is None:
            self.show_alert("Please start scan! Don't have a data to send")
            print(f"[{self.get_timestamp()}] ❌ ยังไม่ได้เริ่มสแกน")
            return

        elif self.status_aoa is None or self.status_rssi is None:
            self.show_alert("Error", "BLE disconnected or failed to send data.")
            print(f"[{self.get_timestamp()}] ❌ BLE ยังไม่เชื่อมต่อ")
            return

        # ส่งข้อมูล Point
        if not self.scanned_point:
            self.scanned_point = []

        url_point = "http://192.168.100.196:5000/rssi_data"
        for device in self.scanned_point:
            data = {"point": device.get('point')}
            print(f"[{self.get_timestamp()}] 📍 กำลังส่ง Point: {data}")
            try:
                response = requests.post(url_point, json=data)
                response.raise_for_status()
                Logger.info(f"✅ ส่ง point สำเร็จ: {response.json()}")
            except requests.exceptions.HTTPError as http_err:
                Logger.error(f'HTTP error occurred: {http_err}')
            except Exception as err:
                Logger.error(f'Other error occurred: {err}')

        # ส่งข้อมูล RSSI/Anchor
        url_datalist = "http://192.168.100.196:5000/rssi_data_list"
        if not self.scanned_devices:
            print(f"[{self.get_timestamp()}] ⚠️ ไม่มี scanned_devices ให้ส่ง")
        else:
            for device in self.scanned_devices:
                data = {
                    "uuid": device.get('uuid'),
                    "rssi": device.get('rssi'),
                    "anchor_id": device.get('anchor_id')
                }
                print(f"[{self.get_timestamp()}] 📶 กำลังส่ง RSSI ข้อมูล: {data}")
                try:
                    response = requests.post(url_datalist, json=data)
                    response.raise_for_status()
                    Logger.info(f"✅ ส่ง RSSI สำเร็จ: {response.json()}")
                except requests.exceptions.HTTPError as http_err:
                    Logger.error(f'HTTP error occurred: {http_err}')
                except Exception as err:
                    Logger.error(f'Other error occurred: {err}')

        # แสดงผลในแอป
        self.root.ids.status.text = "✅ Data Sent"
        self.root.ids.status2.text = "✅ Data Sent"
        print(f"[{self.get_timestamp()}] 🎉 ส่งข้อมูลทั้งหมดเรียบร้อยแล้ว")


        
    def close_application(self):
        App.get_running_app().stop()
        '''main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
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
        '''
        # สร้าง bridge และเริ่มต้น
        
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
            if hasattr(self, 'connected_gatt_uuids') is False:
                self.connected_gatt_uuids = set()

            if self.current_device_uuid in self.connected_gatt_uuids:
                Logger.info(f"🔁 UUID {self.current_device_uuid[:8]}... already connected. Skipping GATT connection.")
                self.update_label(f"GATT Already Connected\nDevice: {self.current_device_uuid}")
                return  # ออกจากฟังก์ชันทันที

            Logger.info(f"BluetoothGATTApp: Connecting GATT to device: {self.current_device_uuid}")
            
            # เชื่อม GATT ใหม่
            self.bridge.startConnectionForDevice_(objc_str(self.current_device_uuid))
            self.bridge.startPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            self.gatt_connected = True
            self.connected_gatt_uuids.add(self.current_device_uuid)  # บันทึก UUID ว่าเคยเชื่อมแล้ว
            
            self.update_label(f"GATT Connecting...\nDevice: {self.current_device_uuid}")
            
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
        self.root.ids.label.text =  text

    @mainthread
    def check_discovered_device(self, dt):
        try:
            device = self.bridge.getLastDiscoveredDevice()
            if not device:
                return

            # ดึงข้อมูลจาก device
            device_name = device.objectForKey_(objc_str("name")).UTF8String()
            device_uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
            device_rssi = device.objectForKey_(objc_str("rssi")).intValue()
            device_major = device.objectForKey_(objc_str("major")).intValue()
            device_minor = device.objectForKey_(objc_str("minor")).intValue()

            if isinstance(device_name, bytes):
                device_name = device_name.decode('utf-8')
            if isinstance(device_uuid, bytes):
                device_uuid = device_uuid.decode('utf-8')

            device_uuid_clean = device_uuid.replace("-", "").upper()

            Logger.info(f"🔍 Found: {device_name}, UUID: {device_uuid[:8]}..., Major: {device_major}, RSSI: {device_rssi}")

            # 🔍 ตรวจว่าเป็น Target หรือไม่
            is_target_device = any(
                target["uuid"].upper() == device_uuid_clean and target["major"] == device_major 
                for target in self.target_data_set
            )

            # ✅ ตรวจซ้ำ
            if is_target_device:
                key = (device_uuid_clean, device_major)
                if key in self.seen_target_devices:
                    Logger.info(f"⏩ Already processed device {device_uuid[:8]}..., Major: {device_major}, skipping...")
                    return  # ❌ ไม่เก็บซ้ำ

                self.seen_target_devices.add(key)  # ✅ เพิ่มเข้า set

                Logger.info(f"🎯 TARGET DEVICE FOUND! UUID: {device_uuid[:8]}..., Major: {device_major}")
                self.current_device_uuid = device_uuid
                self.found_data.add((device_uuid, device_major, device_rssi))
                self.scan_results.append((device_uuid, device_major, device_rssi))

                if device_uuid not in self.gatt_connected_devices:
                    Logger.info(f"🔗 Auto-connecting GATT to target device {device_uuid[:8]}...")
                    self.auto_connect_gatt(device_uuid)
                    self.gatt_connected_devices.add(device_uuid)

                self.display_target_device_info(device_name, device_uuid, device_rssi, device_major, device_minor)

            else:
                display_text = f"📱 Device: {device_name}\n"
                display_text += f"🆔 UUID: {device_uuid[:8]}...\n"
                display_text += f"📶 RSSI: {device_rssi} dBm\n"
                display_text += f"🔢 Major: {device_major} | Minor: {device_minor}\n"
                display_text += f"❌ Not a target device"
                self.root.ids.label.text = display_text
                Logger.info(f"❌ Not target device: {device_name}")

        except Exception as e:
            Logger.error(f"Error in check_discovered_device: {e}")



    def display_target_device_info(self, name, uuid, rssi, major, minor):
        """แสดงข้อมูล target device"""
        try:
            # หยุดแสดงผลถ้าครบ 4 เครื่องแล้ว
            if len(self.found_data) >= 4:
                self.root.ids.label.text = "✅ Connected 4 devices"
                
                # 🚫 หยุดการสแกน BLE - ใช้ method อื่น
                Logger.info("🔄 Attempting to stop BLE scan...")
                try:
                    # ลองใช้ method อื่นที่มีอยู่
                    self.bridge.stopBluetoothScan()  # หรือ
                    # self.bridge.performFullDeviceScan()  # หยุดแล้วเริ่มใหม่
                    Logger.info("✅ Scan stopped successfully")
                except Exception as e:
                    Logger.error(f"❌ Error stopping scan: {e}")
                
                Logger.info("🛑 BLE scan stopped - 4 target devices found")
                return

            display_text = f"🎯 TARGET DEVICE FOUND!\n"
            display_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            display_text += f"📱 Device: {name}\n"
            display_text += f"🆔 UUID: {uuid[:8]}...\n"
            display_text += f"📶 RSSI: {rssi} dBm\n"
            display_text += f"🔢 Major: {major} | Minor: {minor}\n"
            display_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            # แสดงสถานะ GATT
            if self.gatt_connected:
                display_text += f"🔗 GATT: ✅ Connected\n"
                display_text += f"📶 RSSI Monitoring: Active\n"
            else:
                display_text += f"🔗 GATT: 🔄 Connecting...\n"
            
            # แสดงข้อมูลที่พบทั้งหมด
            display_text += f"\n📊 Found Devices: {len(self.found_data)}/4\n"
            
            # แสดงรายการ target ที่พบแล้ว
            found_targets = []
            for uuid_found, major_found, rssi_found in self.found_data:
                target_name = self.get_target_name(uuid_found, major_found)
                found_targets.append(f"{target_name}: {rssi_found}dBm")
            
            if found_targets:
                display_text += f"✅ Found: {', '.join(found_targets)}"
            
            self.root.ids.label.text = display_text

        except Exception as e:
            Logger.error(f"Error displaying target device info: {e}")


    def get_target_name(self, uuid, major):
        """แปลง UUID เป็นชื่อ Anchor (ไม่สนใจ major เพราะ iPhone ส่งมาเป็น 0)"""
        try:
            if uuid.upper() == "A7E39D7510F2FE254DAE4230DBC6C3A4":
                return f"A1 (Major: {major})"
            elif uuid.upper() == "D2F287A95EC6EE4FFD170F5EC006DFAE":
                return f"A2 (Major: {major})"
            elif uuid.upper() == "18DC32EBBD664931152AD431D364E262":
                return f"A3 (Major: {major})"
            elif uuid.upper() == "3D5B8940B5CC24585A5612F6DB393A91":
                return f"A3 (Major: {major})"
            else:
                return f"Unknown (Major: {major})"
        except:
            return "Unknown"
        
    def auto_connect_gatt(self, uuid):
        """เชื่อมต่อ GATT อัตโนมัติเมื่อพบ target device"""
        try:
            if isinstance(uuid, bytes):
                uuid = uuid.decode('utf-8')
            uuid = uuid.upper()

            Logger.info(f"🔗 Starting auto GATT connection to: {uuid[:8]}...")
            
            self.bridge.startConnectionForDevice_(objc_str(uuid))
            self.gatt_connected = True
            
            Clock.schedule_once(lambda dt: self.check_auto_connection_status(uuid), 3.0)
            
            Logger.info("✅ Auto GATT connection initiated")
            
        except Exception as e:
            Logger.error(f"❌ Auto GATT connection failed: {e}")
            self.root.ids.status.text = f"GATT Error: {str(e)[:30]}..."

    def check_auto_connection_status(self, uuid):
        """ตรวจสอบสถานะการเชื่อมต่อ GATT อัตโนมัติ"""
        try:
            is_connected = self.bridge.isDeviceConnected_(objc_str(uuid))
            # ลบบรรทัดนี้ออก เพราะไม่มี method นี้
            # connection_state = self.bridge.getConnectionState(objc_str(uuid))

            Logger.info(f"Auto Connection Status: Connected: {is_connected}")

            if is_connected:
                Logger.info("✅ Auto GATT connection successful!")

                # เริ่ม Real-time RSSI monitoring
                self.start_auto_rssi_monitoring()

                # อัพเดท status
                self.root.ids.status.text = "GATT Connected - Monitoring RSSI"
                self.root.ids.status2.text = "GATT Connected - Monitoring RSSI"

            else:
                Logger.warning("❌ Auto GATT connection failed")
                self.gatt_connected = False
                self.root.ids.status.text = "GATT Failed"
                self.root.ids.status2.text = "GATT Failed"

        except Exception as e:
            Logger.error(f"Error checking auto connection status: {e}")


    def start_auto_rssi_monitoring(self):
        """เริ่ม RSSI monitoring อัตโนมัติหลังเชื่อมต่อ GATT"""
        try:
            if not self.current_device_uuid:
                return
                
            Logger.info("📶 Starting auto RSSI monitoring...")
            
            # ตั้งค่า flag
            self.rssi_monitoring = True
            self.rssi_update_count = 0
            
            # เริ่ม periodic RSSI updates
            self.bridge.startPeriodicRSSIUpdatesForDevice_(objc_str(self.current_device_uuid))
            
            # Schedule การอัพเดท RSSI ทุก 2 วินาที
            if hasattr(self, 'auto_rssi_event'):
                self.auto_rssi_event.cancel()
                
            self.auto_rssi_event = Clock.schedule_interval(self.update_auto_rssi, 2.0)
            
            Logger.info("✅ Auto RSSI monitoring started")
            
        except Exception as e:
            Logger.error(f"Error starting auto RSSI monitoring: {e}")
        
    # def update_auto_rssi(self, rssi_value):
    #     """
    #     ฟังก์ชันนี้ถูกเรียกเพื่ออัปเดตค่าระดับสัญญาณ RSSI แบบอัตโนมัติ
    #     """
    #     Logger.info(f"Received RSSI update: {rssi_value}")
            
        # ตัวอย่างอัปเดตข้อความบน UI หรือประมวลผลข้อมูล RSSI ต่อ
        self.root.ids.status.text = f"RSSI: {rssi_value}"
    # def check_discovered_device(self, dt):
    #     """เช็ค device ที่เจอใหม่"""
    #     device = self.bridge.getLastDiscoveredDevice()
    #     if device:
    #         name = device.objectForKey_(objc_str("name")).UTF8String()
    #         uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
    #         rssi = device.objectForKey_(objc_str("rssi")).intValue()
    #         major = device.objectForKey_(objc_str("major")).intValue()
    #         minor = device.objectForKey_(objc_str("minor")).intValue()

    #         # เก็บ UUID ล่าสุด
    #         self.current_device_uuid = uuid

    #         # แสดงข้อมูล device พร้อมสถานะ GATT
    #         display_text = f"Device: {name}\nUUID: {uuid}\nRSSI: {rssi}\nMajor: {major} Minor: {minor}"
    #         display_rssi = f"RSSI: {rssi}"
    #         # เพิ่มข้อมูลสถานะ GATT
    #         if self.gatt_connected:
    #             connection_state = self.bridge.getConnectionStateForDevice_(objc_str(uuid))
    #             display_text += f"\nGATT State: {connection_state}"
    #         else:
    #             display_text += f"\nGATT: Not Connected"
            
    #         # เพิ่มข้อมูลสถานะระบบ
    #         connected_count = self.bridge.getConnectedDevicesCount()
    #         is_scanning = self.bridge.isScanning()
            
    #         display_text += f"\n\nSystem Status:"
    #         display_text += f"\nConnected: {connected_count}"
    #         display_text += f"\nScanning: {is_scanning}"
            
    #         #self.root.ids.label.text = display_text
    #         self.root.ids.label.text = display_rssi

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
    '''def test_after_start():
        #Clock.schedule_once(lambda dt: app.test_all_gatt_methods(), 5.0)
    
    test_after_start()'''
    app.run()