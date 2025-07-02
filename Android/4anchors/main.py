# android
from jnius import autoclass
import jnius_config

# window
# import asyncio
# import threading
# from bleak import BleakScanner

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.metrics import dp
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
from math import radians, cos, sin
from kivy.core.window import Window
import sys
import pandas as pd
import openpyxl
from kivy.resources import resource_find
import os
from kivy.logger import Logger

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
                on_press: app.start_service()
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
                        
        MDBottomNavigationItem:
            name: 'screen 3'
            text: 'Map'
            icon: 'map-legend'
            on_tab_press: app.plot_initial_point()  # เรียก

            ScreenManager:
                Screen:
                    name: 'image_screen'
                    
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height  # Allow it to adjust height based on content
        
                        # use MapWidget for map
                        MapWidget:
                            id: map_widget
                            size_hint: (1, None) 
                            height: dp(650)  
                        
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint_y: None
                            height: "20dp"  # Set height for button row
                            spacing: 40  
                            padding: [10, 10]  
                            
                            # spacer
                            Widget:
                                size_hint_x: 0.2

                            MDRaisedButton:
                                text: "Grid"
                                size_hint_x: None
                                on_release: map_widget.display_grid()
                                
                            MDRaisedButton:
                                text: "Pos."
                                size_hint_x: None
                                on_release: map_widget.toggle_labels()

                            MDRaisedButton:
                                text: "Angle(L)"
                                size_hint_x: None
                                on_release: map_widget.draw_lines_by_angle_L()

                            MDRaisedButton:
                                text: "Angle(R)"
                                size_hint_x: None
                                on_release: map_widget.draw_lines_by_angle_R()
                                
                            # spacer
                            Widget:
                                size_hint_x: 0.2
                                             
        MDBottomNavigationItem:
            name: 'screen 4'
            text: 'Table'
            icon: 'table'

            MDLabel:
                id: text1
                text: "Table"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_style: "H4"
                pos_hint: {"center_x": .5, "center_y": .85}
                opacity: 1
                
            MDLabel:
                id: text2
                text: "AoA & RSSI"
                size_hint: 0.5, 0.1
                halign: "center"
                bold: True
                font_style: "H6"
                pos_hint: {"center_x": .5, "center_y": .78}
                opacity: 1

            MDLabel:
                id: wait_label
                text: ""
                size_hint_y: None
                font_size: "16sp"
                halign: "center"
                pos_hint: {"center_x": .5, "center_y": .50}
                opacity: 0  # ซ่อนไว้ก่อน
                
            #ScreenManager for ClientsTable and MapWidget_Point
            ScreenManager:
                id: screen_manager
                ClientsTable:
                MapScreen:

            MDRaisedButton:
                id: load_data_btn
                text: "Load Data"
                text_color: "black"
                on_release: app.load_data()
                pos_hint: {"center_x": .5, "center_y": .075}

        MDBottomNavigationItem:
            name: 'screen 5'
            text: 'Info'
            icon: 'information'
            MDCard:
                ripple_behavior: False
                md_bg_color: app.theme_cls.primary_light
                size_hint: 0.7, 0.6
                pos_hint: {"center_x": .5, "center_y": .5}
                MDLabel
                    id: info
                    font_style: "H5"
                    text: "App Info"
                    theme_text_color: "Custom"
                    halign: "center"
                    # pos_hint: {"center_x": .3, "center_y": .9}
                MDLabel
                    id: info2
                    text: "This Application Using Bleak and ABLE Bluetooth"
                    theme_text_color: "Custom"
                    halign: "center"
                    # pos_hint: {"center_x": .3, "center_y": .5}
<ClientsTable>:
    name: 'Clientstable'

<MapScreen>:
    name: 'map_screen'
    
    MDCard:
        ripple_behavior: False
        md_bg_color: app.theme_cls.primary_light
        size_hint: 0.2, 0.065
        pos_hint: {"center_x": .60, "center_y": .96}
        # pos_hint: {"center_x": .60, "center_y": .70}
        MDLabel
            id: label_point_map
            theme_text_color: "Custom"
            size_hint: 0.2, 0.08
            halign: "center"
            pos_hint: {"center_x": .60, "center_y": .96}
                
    # Dropdown Menu
    MDRaisedButton:
        id: menu_button_map
        text: "Point"
        on_release: app.open_menu_map(root.ids.menu_button_map)
        pos_hint: {"center_x": .40, "center_y": .96}
        # pos_hint: {"center_x": .40, "center_y": .70}
        
    MapWidget_Point:
        id: map_point
        size_hint: (1, None)
        height: dp(650)
            
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "20dp"  # Set height for button row
        spacing: 40  
        padding: [10, 10]  

        # spacer
        Widget:
            size_hint_x: 0.2
            
        MDRaisedButton:
            text: "<"
            size_hint_x: None
            on_release: root.manager.current = 'Clientstable'

        MDRaisedButton:
            text: "Grid"
            size_hint_x: None
            on_release: map_point.display_grid()
            
        MDRaisedButton:
            text: "Pos."
            size_hint_x: None
            on_release: map_point.toggle_position_labels()
            
        # spacer
        Widget:
            size_hint_x: 0.2
                    
'''
class MapScreen(Screen):
    pass

class DemoPage(Screen):
    pass

sm = ScreenManager()
sm.add_widget(DemoPage(name='demopage'))

# รันบนWindow
# if platform == "window":
# class MapWidget(Widget):
#     def __init__(self, **kwargs):
#         super(MapWidget, self).__init__(**kwargs)
        
#         # add map picture
#         self.image = Image(source='image_new.png', allow_stretch=True, keep_ratio=True)
#         self.image.size_hint = (None, None)  
#         self.image.size = (self.width, self.height) 
#         self.image.pos_hint = {"center_x": .5, "top": 0.5}  
#         self.add_widget(self.image)
        
#         self.labels = []
#         self.grid_drawn = False
#         self.grid_lines = []
        
#         self.angle_drawn_L = False
#         self.angle_lines_L = []
#         self.angle_drawn_R = False
#         self.angle_lines_R = []
        
#         self.start_L_x, self.start_L_y = 131, 405
#         self.start_R_x, self.start_R_y = 907, 405
        
#         # Initialize labels but don't add them to the widget yet
#         self.coord_label_L = Label(text=f"(0, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
#         self.coord_label_R = Label(text=f"(14.924, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
#         self.coord_label_P = Label(text=f"(0, 0)", size_hint=(None, None), color=(1, 0, 0, 1), font_size=24)        

#         # use canvas to draw
#         with self.canvas:
#             # ตั้งสีของกรอบ
#             # Color(0, 1, 0, 1)  # สีเขียว
#             # วาดเส้นกรอบสี่เหลี่ยมรอบจุด
#             # self.rect = Line(rectangle=(131, 345, 776, 990), width=1.5)  
            
#             Color(0, 0, 0, 1) # สีดำ
#             self.point_A1 = Ellipse(pos=(self.start_L_x-5, self.start_L_y-5), size=(15, 15))  
#             self.point_A2 = Ellipse(pos=(self.start_R_x-5, self.start_R_y-5), size=(15, 15))  
#             Color(1, 0, 0, 1) # สีแดง
#             self.point_Estimate = Ellipse(pos=(100, 100), size=(20, 20))  

#     def on_size(self, *args):
#         # เมื่อขนาดของ MapWidget เปลี่ยนแปลง จะอัปเดตขนาดของภาพให้เข้ากับ MapWidget
#         self.image.size = (self.width, self.height)  # ตั้งขนาดให้เท่ากับขนาดของ MapWidget
#         self.image.pos_hint = {"center_x": .5, "top": 0.5} 
        
#     def toggle_labels(self):
#         if not self.coord_label_L.parent:  # Check if the label is not displayed
#             self.coord_label_L.pos = (self.start_L_x - 48, self.start_L_y - 75)
#             self.coord_label_R.pos = (self.start_R_x - 48, self.start_R_y - 75)
#             self.add_widget(self.coord_label_L)  # Add 
#             self.add_widget(self.coord_label_R)
#             self.add_widget(self.coord_label_P)
#         else:
#             self.remove_widget(self.coord_label_L)  # Remove 
#             self.remove_widget(self.coord_label_R)
#             self.remove_widget(self.coord_label_P)
    
#     # Draw the grid
#     def display_grid(self):
#         if not self.grid_drawn:
#             with self.canvas:
#                 Color(0.5, 0.5, 0.5, 1) # สีดำ
#                 num_cells_x = int(14.924 / 0.5)
#                 num_cells_y = int(18.191 / 0.5)
#                 grid_width = int(776 / num_cells_x) * 2
#                 grid_height = int(990 / num_cells_y) * 2
#                 width = 907 #14.924
#                 height = 1395 #18.191
                
#                 for x in range(self.start_L_x, width + grid_width, grid_width):
#                     line = Line(points=[x, self.start_L_y, x, height + 36], width=1)
#                     self.grid_lines.append(line)
#                 for y in range(self.start_R_y, height + grid_height, grid_height):
#                     line = Line(points=[self.start_L_x, y, width + 4, y], width=1)
#                     self.grid_lines.append(line)
                
#             self.grid_drawn = True
            
#         else:
#             # Clear all grid lines
#             for line in self.grid_lines:
#                 self.canvas.remove(line)
#             self.grid_lines.clear()
            
#             self.grid_drawn = False
            
#     def draw_lines_by_angle_L(self):
#         if not self.angle_drawn_L:
#             length_line = 1300

#             with self.canvas:
#                 Color(0, 0, 1, 1)  # สีน้ำเงิน
#                 for angle in range(0, 100, 10):
#                     radians_angle = radians(angle)
#                     end_L_x = self.start_L_x + length_line * cos(radians_angle)  
#                     end_L_y = self.start_L_y + length_line * sin(radians_angle)
#                     line = Line(points=[self.start_L_x, self.start_L_y, end_L_x, end_L_y], width=1)
#                     self.angle_lines_L.append(line)
            
#             self.angle_drawn_L = True
#         else:
#             # Clear all angle lines
#             for line in self.angle_lines_L:
#                 self.canvas.remove(line)
#             self.angle_lines_L.clear()
#             self.angle_drawn_L = False
            
#     def draw_lines_by_angle_R(self):
#         if not self.angle_drawn_R:
#             length_line = 1300
                    
#             with self.canvas:
#                 Color(1, 0, 1, 1) # สีม่วง
#                 for angle in range(0, 100, 10):
#                     radians_angle = radians(angle)
#                     end_R_x = self.start_R_x - length_line * cos(radians_angle)  
#                     end_R_y = self.start_R_y + length_line * sin(radians_angle)
#                     line = Line(points=[self.start_R_x+4, self.start_R_y, end_R_x+4, end_R_y], width=1)
#                     self.angle_lines_R.append(line)
            
#             self.angle_drawn_R = True
#         else:
#             # Clear all angle lines
#             for line in self.angle_lines_R:
#                 self.canvas.remove(line)
#             self.angle_lines_R.clear()
#             self.angle_drawn_R = False
            
#     # ฟังก์ชันสำหรับพล็อตจุดใหม่
#     def plot_point(self, x, y, real_coord):
#         # อัปเดตพิกัดของจุด
#         self.point_Estimate.pos = (x-10, y-15)
        
#             # Update the label estimated coordinates
#         self.coord_label_P.text = f"({real_coord[0]}, {real_coord[1]})"
#         self.coord_label_P.pos = (x-48, y-78)

# class ClientsTable(Screen):
#     def load_table(self):
#         layout = AnchorLayout()
#         devices = asyncio.run(self.async_scan_devices())
#         for device in devices:
#             name = device.name
#             rssi = device.rssi
#             if name in self.target_device_names:
#                 self.data_tables = MDDataTable(
#                     pos_hint={'center_y': 0.5, 'center_x': 0.5},
#                     size_hint=(0.6, 0.8),
#                     use_pagination=True,
#                     check=True,
#                     column_data=[
#                         ("No.", dp(30)),
#                         ("Name", dp(30)),
#                         ("RSSI", dp(30)), ],
#                     row_data=[
#                         (f"{i + 1}", f"{name}", f"{rssi}")
#                         for i in range(5)], )
#         self.add_widget(self.data_tables)
#         return layout
        
#     async def async_scan_devices(self):
#         scanner = BleakScanner()
#         self.target_device_names = ["P2N_09725", "P2N_09714", "ZLB_39612"]
#         scanner.device_filter = lambda device: device.name in self.target_device_names
#         return await scanner.discover()

#     def on_enter(self):
#         self.load_table()

# sm = ScreenManager()
# sm.add_widget(DemoPage(name='demopage'))
# sm.add_widget(ClientsTable(name='Clientstable'))

# class MyApp(MDApp):
#     def build(self):
#         self.theme_cls.theme_style = "Dark"
#         self.theme_cls.primary_palette = "Amber"
#         self.scanning = False
#         self.target_device_names = ["P2N_09725", "P2N_09714", "ZLB_39612"]
#         return Builder.load_string(KV)
    
#     def switch_theme_style(self):
#         self.theme_cls.primary_palette = ("Orange" if self.theme_cls.primary_palette == "Blue" else "Blue")
#         self.theme_cls.theme_style = ("Dark" if self.theme_cls.theme_style == "Light" else "Light")

#     def close_application(self):
#         App.get_running_app().stop()

#     def start_service(self):
#         if not self.scanning:
#             self.root.ids.label.text = ""  # Clear the previous scan results
#             self.scanning = True
#             Logger.info('Bluetooth: Scanning...')
#             threading.Thread(target=self.scan_devices).start()

#     def scan_devices(self):
#         self.root.ids.status.text = "Scanning..."
#         devices = asyncio.run(self.async_scan_devices())
#         Clock.schedule_once(lambda dt: self.display_scan_results(devices), 0)
#         self.scanning = False

#     async def async_scan_devices(self):
#         scanner = BleakScanner()
#         scanner.device_filter = lambda device: device.name in self.target_device_names
#         return await scanner.discover()
    
#     def calculate_distance(self, rssi, RSSI_0, n):
#         ratio = (RSSI_0-rssi)/(10*n)
#         return math.pow(10,ratio)
    
#     def trilateration(self, d1, d2, d3, x1, y1, x2, y2, x3, y3):
#             A = x1**2 + y1**2 - d1**2
#             B = x2**2 + y2**2 - d2**2
#             C = x3**2 + y3**2 - d3**2

#             X32 = x3 - x2
#             X13 = x1 - x3
#             X21 = x2 - x1

#             Y32 = y3 - y2
#             Y13 = y1 - y3
#             Y21 = y2 - y1

#             xe = (A * Y32 + B * Y13 + C * Y21) / (2 * (x1 * Y32 + x2 * Y13 + x3 * Y21))
#             ye = (A * X32 + B * X13 + C * X21) / (2 * (y1 * X32 + y2 * X13 + y3 * X21))

#             return xe, ye
    
#     def display_scan_results(self, devices):
#         self.scanned_devices = []  # ล้างข้อมูลอุปกรณ์ที่สแกนก่อนหน้านี้
#         scanned_info = ''
#         n = 2

#         # RSSI_0 values for each anchor
#         RSSI_0_values = {
#             "P2N_09714": -51,
#             "P2N_09725": -54,
#             "ZLB_39612": -51
#         }
        
#         # กำหนด anchors และตำแหน่ง
#         anchors = {
#             "P2N_09714": (3.506, 2.382),
#             "P2N_09725": (0, 11.244),
#             "ZLB_39612": (5.725, 9.955)
#         }
        
#         # สร้างรายการเพื่อเก็บค่า RSSI และระยะทางที่คำนวณได้
#         distances = []
#         rssi_values = []
#         positions = []

#         for device in devices:
#             name = device.name
#             if name in anchors:  # ตรวจสอบว่าอุปกรณ์เป็น anchor ที่กำหนด
#                 rssi = device.rssi
#                 RSSI_0 = RSSI_0_values[name]  
#                 distance = self.calculate_distance(rssi, RSSI_0, n)
#                 distances.append(distance)
#                 rssi_values.append(rssi)
#                 positions.append(anchors[name])

#                 scanned_info += f"{name}, RSSI: {rssi} dBm, Distance: {distance:.2f} m\n"
#                 self.scanned_devices.append({"name": name, "rssi": rssi, "distance": distance})

#         # ตรวจสอบว่ามีค่าระยะทางครบสามค่าเพื่อคำนวณ trilateration
#         if len(distances) >= 3:
#             x1, y1 = positions[0]
#             x2, y2 = positions[1]
#             x3, y3 = positions[2]
#             d1, d2, d3 = distances[0], distances[1], distances[2]

#             x, y = self.trilateration(d1, d2, d3, x1, y1, x2, y2, x3, y3)
#             scanned_info += f"positions: ({x:.3f}, {y:.3f})\n"

#             self.scanned_devices.append({"name": "Trilateration Result", "position": (x, y)})
            
#         self.root.ids.label.text = scanned_info
#         self.root.ids.status.text = "Scan Complete"
#         Logger.info('Bluetooth: ' + '\n' + scanned_info)
        
#     def calculate_real_to_pixel(self, x_real, y_real):
#         origin_x = 131 
#         origin_y = 405 
#         width = 776 
#         height = 990 
#         real_width = 14.924 
#         real_height = 18.191
        
#         scale_x = width / real_width  # อัตราส่วนพิกเซลต่อเมตรในแนวนอน
#         scale_y = height / real_height  # อัตราส่วนพิกเซลต่อเมตรในแนวตั้ง

#         # แปลงพิกัดจริงเป็นพิกัดพิกเซล
#         x_pixel = origin_x + (x_real * (scale_x))
#         y_pixel = origin_y + (y_real * (scale_y))

#         return x_pixel, y_pixel
    
#     def plot_initial_point(self):
#         # พิกัดจริงที่ต้องการแปลง
#         real_coordinate = (8.75, 16)
#         map_coordinate = self.calculate_real_to_pixel(*real_coordinate)    

#         # พล็อตจุดที่ตำแหน่ง
#         map_widget = self.root.ids.map_widget
#         map_widget.plot_point(*map_coordinate, real_coordinate) 

#     def send_data(self):
#         self.scanning = False
#         self.root.ids.status.text = "Sending data..."
#         for device in self.scanned_devices:
#             # Check if "rssi" key exists in the device dictionary
#             if "rssi" in device:
#                 rssi = device["rssi"]
#             else:
#                 rssi = None
        
#             # Check if "position" key exists in the device dictionary
#             if "position" in device:
#                 x, y = device["position"]
#                 self.send_data_to_api(device["name"], rssi, device.get("distance", None), x, y)
#             else:
#                 self.send_data_to_api(device["name"], rssi, device.get("distance", None))
                
#         self.root.ids.status.text = "Send data Complete"
#         Logger.info('Bluetooth: Send data Complete')
        
#     def send_data_to_api(self, name, rssi, distance, x=None, y=None):
#         url = "http://192.168.100.49:5000/Input"  # Replace with your actual API endpoint
#         if distance is not None:
#             distance = "%.3f" % distance
#         else:
#             distance = None
            
#         if x is not None and y is not None:
#             x = "%.3f" % x
#             y = "%.3f" % y
#         else:
#             x = None
#             y = None
            
#         data = {
#             "anc_name": name,
#             "rssi": rssi,
#             "distance": distance,
#             "x": x,
#             "y": y
#         }
    
#         try:
#             response = requests.post(url, json=data)
#             response.raise_for_status()
#             Logger.info(f'Successfully sent data to API: {response.json()}')
#         except requests.exceptions.HTTPError as http_err:
#             Logger.error(f'HTTP error occurred: {http_err}')
#         except Exception as err:
#             Logger.error(f'Other error occurred: {err}')
            
#     def stop_service(self):
#         self.scanning = False
#         self.root.ids.status.text = "Stop Scanning"
#         Logger.info('Bluetooth: Stop Scanning')
            
# if __name__ == "__main__":
#     MyApp().run()

# รันบนมือถือ Android
if platform == 'android':
    from able import GATT_SUCCESS, BluetoothDispatcher, require_bluetooth_enabled
    jnius_config.set_classpath('org/able/BLE.jar')
    jnius_config.set_classpath('org/able/BLEAdvertiser.jar')
    jnius_config.set_classpath('org/able/PythonBluetooth.jar')
    jnius_config.set_classpath('org/able/PythonBluetoothAdvertiser.jar')
    autoclass('org.able.BLE')
    autoclass('org.able.BLEAdvertiser')
    autoclass('org.able.PythonBluetooth')
    autoclass('org.able.PythonBluetoothAdvertiser')
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    class MapWidget(Widget):
        def __init__(self, **kwargs):
            super(MapWidget, self).__init__(**kwargs)
            self.text_item = None
            self.last_text_item = self.text_item
            
            # add map
            self.image = Image(source='image_new.png', allow_stretch=True, keep_ratio=True)
            self.image.size_hint = (None, None)
            self.image.size = (self.width, self.height)
            self.image.pos_hint = {"center_x": .5, "top": 0.5}  
            self.add_widget(self.image)
            ##add for ios
            #Clock.schedule_once(self.update_image_size, 0)
            
            self.labels = []
            self.grid_drawn = False
            self.grid_lines = []
            
            self.angle_drawn_L = False
            self.angle_lines_L = []
            self.angle_drawn_R = False
            self.angle_lines_R = []
            
            self.start_L_x, self.start_L_y = 131, 405
            self.start_R_x, self.start_R_y = 907, 405
            #-----
            self.start_A_x, self.start_A_y = 302, 927
            self.start_B_x, self.start_B_y = 505, 666
            self.start_C_x, self.start_C_y = 380, 470
            self.start_D_x, self.start_D_y = 708, 486
            self.start_E_x, self.start_E_y = 848, 633
            self.start_F_x, self.start_F_y = 224, 1221
            # self.start_L2_x, self.start_L2_y = 131, 1378
            # self.start_R2_x, self.start_R2_y = 907, 1378
            
            # Initialize labels but don't add them to the widget yet
            self.coord_label_L = Label(text=f"A1(0, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_R = Label(text=f"A2(14.924, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            #-----
            self.coord_label_A = Label(text=f"A(3.3, 9.6)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_B = Label(text=f"B(7.2, 4.8)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_C = Label(text=f"C(4.8, 1.2)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_D = Label(text=f"D(11.1, 1.5)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_E = Label(text=f"E(13.8, 4.2)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_F = Label(text=f"F(1.8, 15.00)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            # self.coord_label_L2 = Label(text=f"(0, 18.191)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            # self.coord_label_R2 = Label(text=f"(14.924, 18.191)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_P = Label(text=f"(0, 0)", size_hint=(None, None), color=(1, 0, 0, 1), font_size=24)        

            # use canvas to draw
            with self.canvas:
                Color(0, 1, 0, 1)  #Green
                #draw square
                self.rect = Line(rectangle=(131, 345, 776, 990), width=1.5)  
                
                Color(0, 0, 0, 1)    #black
                self.point_A1 = Ellipse(pos=(self.start_L_x-5, self.start_L_y-5), size=(15, 15))  
                self.point_A2 = Ellipse(pos=(self.start_R_x-5, self.start_R_y-5), size=(15, 15))
                #-----  
                Color(0, 1, 0, 1)    #Green
                self.pointA = Ellipse(pos=(self.start_A_x-5, self.start_A_y-5), size=(15, 15))  
                self.pointB = Ellipse(pos=(self.start_B_x-5, self.start_B_y-5), size=(15, 15))  
                self.pointC = Ellipse(pos=(self.start_C_x-5, self.start_C_y-5), size=(15, 15))  
                self.pointD = Ellipse(pos=(self.start_D_x-5, self.start_D_y-5), size=(15, 15))  
                self.pointE = Ellipse(pos=(self.start_E_x-5, self.start_E_y-5), size=(15, 15))  
                self.pointF = Ellipse(pos=(self.start_F_x-5, self.start_F_y-5), size=(15, 15))  
                # self.point_A3 = Ellipse(pos=(self.start_L2_x-5, self.start_L2_y-5), size=(15, 15))  
                # self.point_A4 = Ellipse(pos=(self.start_R2_x-5, self.start_R2_y-5), size=(15, 15))  
                Color(1, 0, 0, 1)    #red
                self.point_Estimate = Ellipse(pos=(100, 100), size=(20, 20))  
    
        def on_size(self, *args):
            #if size of MapWidget is change. it will update size to fit MapWidget
            self.image.size = (self.width, self.height)
            self.image.pos_hint = {"center_x": .5, "top": 0.5} 
            
        def toggle_labels(self):
            if not self.coord_label_L.parent:  # Check if the label is not displayed
                self.coord_label_L.pos = (self.start_L_x - 48, self.start_L_y - 75)
                self.coord_label_R.pos = (self.start_R_x - 48, self.start_R_y - 75)
                #-----
                self.coord_label_A.pos = (self.start_A_x - 48, self.start_A_y - 75)
                self.coord_label_B.pos = (self.start_B_x - 48, self.start_B_y - 75)
                self.coord_label_C.pos = (self.start_C_x - 48, self.start_C_y - 75)
                self.coord_label_D.pos = (self.start_D_x - 48, self.start_D_y - 75)
                self.coord_label_E.pos = (self.start_E_x - 48, self.start_E_y - 75)
                self.coord_label_F.pos = (self.start_F_x - 48, self.start_F_y - 75)
                # self.coord_label_L2.pos = (self.start_L2_x - 48, self.start_L2_y - 75)
                # self.coord_label_R2.pos = (self.start_R2_x - 48, self.start_R2_y - 75)
                self.add_widget(self.coord_label_L)  # Add labels when toggled on
                self.add_widget(self.coord_label_R)
                #----
                self.add_widget(self.coord_label_A)
                self.add_widget(self.coord_label_B)
                self.add_widget(self.coord_label_C)
                self.add_widget(self.coord_label_D)
                self.add_widget(self.coord_label_E)
                self.add_widget(self.coord_label_F)
                # self.add_widget(self.coord_label_L2)
                # self.add_widget(self.coord_label_R2)
                self.add_widget(self.coord_label_P)
            else:
                self.remove_widget(self.coord_label_L)  # Remove when toggled off
                self.remove_widget(self.coord_label_R)
                #----
                self.remove_widget(self.coord_label_A)
                self.remove_widget(self.coord_label_B)
                self.remove_widget(self.coord_label_C)
                self.remove_widget(self.coord_label_D)
                self.remove_widget(self.coord_label_E)
                self.remove_widget(self.coord_label_F)
                # self.remove_widget(self.coord_label_L2)
                # self.remove_widget(self.coord_label_R2)
                self.remove_widget(self.coord_label_P)
        
        # Draw the grid
        def display_grid(self):
            if not self.grid_drawn:
                with self.canvas:
                    Color(0.5, 0.5, 0.5, 1) #black
                    num_cells_x = int(14.924 / 0.5)
                    num_cells_y = int(18.191 / 0.5)
                    grid_width = int(776 / num_cells_x) * 2
                    grid_height = int(990 / num_cells_y) * 2
                    width = 907 #14.924
                    height = 1395 #18.191
                    
                    for x in range(self.start_L_x, width + grid_width, grid_width):
                        line = Line(points=[x, self.start_L_y, x, height + 36], width=1)
                        self.grid_lines.append(line)
                    for y in range(self.start_R_y, height + grid_height, grid_height):
                        line = Line(points=[self.start_L_x, y, width + 4, y], width=1)
                        self.grid_lines.append(line)
                    
                self.grid_drawn = True
                
            else:
                # Clear all grid lines
                for line in self.grid_lines:
                    self.canvas.remove(line)
                self.grid_lines.clear()
                
                self.grid_drawn = False
                
        def draw_lines_by_angle_L(self):
            if not self.angle_drawn_L:
                length_line = 1300

                with self.canvas:
                    Color(0, 0, 1, 1)  #blue
                    for angle in range(0, 100, 10):
                        radians_angle = radians(angle)
                        end_L_x = self.start_L_x + length_line * cos(radians_angle)  
                        end_L_y = self.start_L_y + length_line * sin(radians_angle)
                        line = Line(points=[self.start_L_x, self.start_L_y, end_L_x, end_L_y], width=1)
                        self.angle_lines_L.append(line)
                
                self.angle_drawn_L = True
            else:
                # Clear all angle lines
                for line in self.angle_lines_L:
                    self.canvas.remove(line)
                self.angle_lines_L.clear()
                self.angle_drawn_L = False
                
        def draw_lines_by_angle_R(self):
            if not self.angle_drawn_R:
                length_line = 1300
                        
                with self.canvas:
                    Color(1, 0, 1, 1) #purple
                    # Color(0 / 255, 255 / 255, 255 / 255) 
                    for angle in range(0, 100, 10):
                        radians_angle = radians(angle)
                        end_R_x = self.start_R_x - length_line * cos(radians_angle)  
                        end_R_y = self.start_R_y + length_line * sin(radians_angle)
                        line = Line(points=[self.start_R_x+4, self.start_R_y, end_R_x+4, end_R_y], width=1)
                        self.angle_lines_R.append(line)
                
                self.angle_drawn_R = True
            else:
                # Clear all angle lines
                for line in self.angle_lines_R:
                    self.canvas.remove(line)
                self.angle_lines_R.clear()
                self.angle_drawn_R = False
                
        # function for plot new point(calculates)
        def plot_point(self, x, y, real_coord):
            #update point
            self.point_Estimate.pos = (x-10, y-10)
            print(f"position calculate {x},{y}")
            
            #Update the label estimated coordinates
            self.coord_label_P.text = f"({real_coord[0]:.2f}, {real_coord[1]:.2f})"
            self.coord_label_P.pos = (x-48, y-78)
    #-------------------------------------------------------------------------------- 
    #Map of Screen4 (Table)
    class MapWidget_Point(Widget):
        def __init__(self, **kwargs):
            super(MapWidget_Point, self).__init__(**kwargs)
            self.pos_visible = False
            self.position_labels = []
            self.dialog = None
            
            #add map
            self.image = Image(source='image_new.png', allow_stretch=True, keep_ratio=True)
            self.image.size_hint = (None, None)
            self.image.size = (self.width, self.height)
            self.image.pos_hint = {"center_x": .5, "top": 0.5}  
            self.add_widget(self.image)

            self.labels = []
            self.grid_drawn = False
            self.grid_lines = []
            
            self.start_L_x, self.start_L_y = 131, 405
            self.start_R_x, self.start_R_y = 907, 405
            #-----
            self.start_A_x, self.start_A_y = 302, 927
            self.start_B_x, self.start_B_y = 505, 666
            self.start_C_x, self.start_C_y = 380, 470
            self.start_D_x, self.start_D_y = 708, 486
            self.start_E_x, self.start_E_y = 848, 633
            self.start_F_x, self.start_F_y = 224, 1221
            
            self.start_AoA_x, self.start_AoA_y = 58, 197
            self.start_RSSI_x, self.start_RSSI_y = 58, 147
            
            # Initialize labels but don't add them to the widget yet
            self.coord_label_L = Label(text=f"A1(0, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_R = Label(text=f"A2(14.924, 0)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            #-----
            self.coord_label_A = Label(text=f"A(3.3, 9.6)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_B = Label(text=f"B(7.2, 4.8)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_C = Label(text=f"C(4.8, 1.2)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_D = Label(text=f"D(11.1, 1.5)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_E = Label(text=f"E(13.8, 4.2)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            self.coord_label_F = Label(text=f"F(1.8, 15.00)", size_hint=(None, None), color=(0, 0, 0, 1), font_size=24)
            
            self.coord_label_AoA = Label(text=f"AoA", size_hint=(None, None), color=(1, 0, 0, 1), font_size=24)
            self.coord_label_RSSI = Label(text=f"RSSI", size_hint=(None, None), color=(0.5, 0, 0.5, 1), font_size=24)

            # use canvas to draw
            with self.canvas:
                Color(0, 0, 0, 1) #black
                self.point_A1 = Ellipse(pos=(self.start_L_x-5, self.start_L_y-5), size=(15, 15))  
                self.point_A2 = Ellipse(pos=(self.start_R_x-5, self.start_R_y-5), size=(15, 15))
                
                #-----  
                Color(0, 1, 0, 1) #green
                self.pointA = Ellipse(pos=(self.start_A_x-5, self.start_A_y-5), size=(15, 15))  
                self.pointB = Ellipse(pos=(self.start_B_x-5, self.start_B_y-5), size=(15, 15))  
                self.pointC = Ellipse(pos=(self.start_C_x-5, self.start_C_y-5), size=(15, 15))  
                self.pointD = Ellipse(pos=(self.start_D_x-5, self.start_D_y-5), size=(15, 15))  
                self.pointE = Ellipse(pos=(self.start_E_x-5, self.start_E_y-5), size=(15, 15))  
                self.pointF = Ellipse(pos=(self.start_F_x-5, self.start_F_y-5), size=(15, 15))  
                
                Color(1, 0, 0, 1) #red
                self.point_AoA = Ellipse(pos=(self.start_AoA_x-5, self.start_AoA_y-5), size=(15, 15)) 
                Color(0.5, 0, 0.5, 1) #purple 
                self.point_RSSI = Ellipse(pos=(self.start_RSSI_x-5, self.start_RSSI_y-5), size=(15, 15))
                
            # Add labels
            self.coord_label_L.pos = (self.start_L_x - 48, self.start_L_y - 75)
            self.coord_label_R.pos = (self.start_R_x - 48, self.start_R_y - 75)
            self.add_widget(self.coord_label_L)  
            self.add_widget(self.coord_label_R)
                
            self.coord_label_A.pos = (self.start_A_x - 48, self.start_A_y - 75)
            self.coord_label_B.pos = (self.start_B_x - 48, self.start_B_y - 75)
            self.coord_label_C.pos = (self.start_C_x - 48, self.start_C_y - 75)
            self.coord_label_D.pos = (self.start_D_x - 48, self.start_D_y - 75)
            self.coord_label_E.pos = (self.start_E_x - 48, self.start_E_y - 75)
            self.coord_label_F.pos = (self.start_F_x - 48, self.start_F_y - 75)
            self.add_widget(self.coord_label_A)
            self.add_widget(self.coord_label_B)
            self.add_widget(self.coord_label_C)
            self.add_widget(self.coord_label_D)
            self.add_widget(self.coord_label_E)
            self.add_widget(self.coord_label_F)
            
            self.coord_label_AoA.pos = (self.start_AoA_x - 10, self.start_AoA_y - 45)
            self.coord_label_RSSI.pos = (self.start_RSSI_x - 10, self.start_RSSI_y - 45)
            self.add_widget(self.coord_label_AoA)  
            self.add_widget(self.coord_label_RSSI)
            
        def on_size(self, *args):
            #if size of MapWidget is change. it will update size to fit MapWidget
            self.image.size = (self.width, self.height)
            self.image.pos_hint = {"center_x": .5, "top": 0.5} 

        # Draw the grid
        def display_grid(self):
            if not self.grid_drawn:
                with self.canvas:
                    Color(0.5, 0.5, 0.5, 1) # black
                    num_cells_x = int(14.924 / 0.5)
                    num_cells_y = int(18.191 / 0.5)
                    grid_width = int(776 / num_cells_x) * 2
                    grid_height = int(990 / num_cells_y) * 2
                    width = 907 #14.924
                    height = 1395 #18.191
                    
                    for x in range(self.start_L_x, width + grid_width, grid_width):
                        line = Line(points=[x, self.start_L_y, x, height + 36], width=1)
                        self.grid_lines.append(line)
                    for y in range(self.start_R_y, height + grid_height, grid_height):
                        line = Line(points=[self.start_L_x, y, width + 4, y], width=1)
                        self.grid_lines.append(line)
                    
                self.grid_drawn = True
                
            else:
                # Clear all grid lines
                for line in self.grid_lines:
                    self.canvas.remove(line)
                self.grid_lines.clear()
                
                self.grid_drawn = False
                
        #Show notification
        def show_alert_map(self, message):
            if self.dialog is None:
                self.dialog = MDDialog(
                    title="Select Point",
                    text=message,
                    buttons=[
                        MDRaisedButton(
                            text="OK",
                            on_release=lambda x: self.dialog.dismiss()
                        )
                    ]
                )
            else:
                self.dialog.text = message 
            self.dialog.open()
        
        #Hide Label
        def toggle_position_labels(self):
            if not hasattr(self, "plotted_points") or not self.plotted_points:
                self.show_alert_map("Please!! select a Point first")
                return
            
            if self.pos_visible:
                #hide all Label
                for label in self.position_labels:
                    self.remove_widget(label)
                self.position_labels.clear()
            else:
                #show Label
                for text_item, widgets in self.plotted_points.items():
                    for widget in widgets:
                        if isinstance(widget, Label):
                            self.add_widget(widget)
                            self.position_labels.append(widget)
            self.pos_visible = not self.pos_visible  #Switch status
        
        #----------------------------------------------------------------------------------   
        #plot point aoa
        def plot_point_map_aoa(self, x, y, real_coord, text_item):
            #Check if plotted points before.
            if not hasattr(self, "plotted_points"):
                self.plotted_points = {}

            #If text_item changes from the original value Let's delete the old points first
            if hasattr(self, "last_text_item") and self.last_text_item != text_item:
                #delete from last_text_item
                if self.last_text_item in self.plotted_points:
                    for widget in self.plotted_points[self.last_text_item]:
                        self.remove_widget(widget)
                    self.plotted_points[self.last_text_item] = []  #clear

            #update text_item
            self.last_text_item = text_item

            #if text_item don't have in dictionary create list for keep point
            if text_item not in self.plotted_points:
                self.plotted_points[text_item] = []

            #create new point
            new_point = Widget(
                size=(10, 10),
                pos=(x - 10, y - 10)
            )

            with new_point.canvas:
                Color(1, 0, 0, 1)  #red
                Ellipse(pos=new_point.pos, size=new_point.size)

            self.add_widget(new_point)

            #create Label
            new_label = Label(
                text=f"({real_coord[0]:.2f}, {real_coord[1]:.2f})",
                pos=(x - 48, y - 78),
                font_size=15,
                color=(1, 0, 0, 1)
            )

            if self.pos_visible:
                self.add_widget(new_label)
                self.position_labels.append(new_label)

            #save widget that plot in dictionary
            self.plotted_points[text_item].append(new_point)
            self.plotted_points[text_item].append(new_label)
            print(f"Plotted at: {x}, {y}")
            
        #---------------------------------------------------------------------------------- 
        #plot point rssi
        def plot_point_map_rssi(self, x, y, real_coord, text_item):
            #Check if plotted points before.
            if not hasattr(self, "plotted_points"):
                self.plotted_points = {}

            #If text_item changes from the original value Let's delete the old points first
            if hasattr(self, "last_text_item") and self.last_text_item != text_item:
                #delete from last_text_item
                if self.last_text_item in self.plotted_points:
                    for widget in self.plotted_points[self.last_text_item]:
                        self.remove_widget(widget)
                    self.plotted_points[self.last_text_item] = []  #clear

            #update text_item
            self.last_text_item = text_item

            #if text_item don't have in dictionary create list for keep point
            if text_item not in self.plotted_points:
                self.plotted_points[text_item] = []

            #create new point
            new_point = Widget(
                size=(10, 10),
                pos=(x - 10, y - 10)
            )

            with new_point.canvas:
                Color(0.5, 0, 0.5, 1) #purple
                Ellipse(pos=new_point.pos, size=new_point.size)

            self.add_widget(new_point)

            #create Label
            new_label = Label(
                text=f"({float(real_coord[0]):.2f}, {float(real_coord[1]):.2f})",
                pos=(x - 48, y - 78),
                font_size=15,
                color=(0.5, 0, 0.5, 1)
            )
            
            if self.pos_visible:
                self.add_widget(new_label)
                self.position_labels.append(new_label)

            #save widget that plot in dictionary
            self.plotted_points[text_item].append(new_point)
            self.plotted_points[text_item].append(new_label)
            print(f"Plotted at: {x}, {y}")
                
    #---------------------------------------------------------------------------------------------
    #Show Table of Sceen4
    class ClientsTable(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def fetch_data(self,point):
            url = f'http://192.168.100.49:5000/Table_Point' #IP of server to connect database
            params = {'point': point}  #send 'point' to request parameters
            print("Fetching from:", url, "with params:", params)
            response = requests.get(url, params=params)
            print("Response Text:", response.text)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("Data received:", data) 
                    Logger.info(f"Data is : {data}")
                    if data:
                        print("Keys in first data item:", data[0].keys())
                    return data
                except ValueError:
                    Logger.error("Failed to decode JSON")
                    return []
            else:
                Logger.error(f"Failed with status code {response.status_code} from {url}")
                return []
            
        def go_to_map(self, *args):
            self.manager.current = 'map_screen'

        def load_table(self):
            #creat main Layout
            main_layout = MDBoxLayout(orientation="vertical", size_hint=(1, 1))

            #Header 
            header_label = MDLabel(
                text="Table: AoA & RSSI",
                halign="center",
                bold=True,
                font_style="H4",
                size_hint_y=None,
                height=dp(50),
                padding=(0, dp(10))
            )
            main_layout.add_widget(header_label)

            #creat ScrollView
            scroll_view = ScrollView(size_hint=(1, 1))

            #Layout in ScrollView
            layout = MDBoxLayout(orientation="vertical", size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))  # ทำให้ ScrollView ทำงาน

            #button Go to Map
            button = MDRaisedButton(
                text="Go to Map",
                size_hint=(0.2, None),
                height=dp(40),
                pos_hint={'center_x': 0.5}
            )
            button.bind(on_release=self.go_to_map)
            layout.add_widget(button)

            point_list = ['A', 'B', 'C', 'D', 'E', 'F']

            for point in point_list:
                # เพิ่มหัวข้อสำหรับแต่ละตาราง
                sub_header_label = MDLabel(
                    text=f"• Point {point} •",
                    halign="center",
                    bold=True,
                    size_hint=(1, None),
                    height=dp(40),
                    font_size="16sp"
                )
                layout.add_widget(sub_header_label)

                data = self.fetch_data(point)
                row_data = [
                    (str(j + 1), client.get("Point", "Unknown"),
                    str(client.get("X_AoA", "N/A")), str(client.get("Y_AoA", "N/A")),
                    str(client.get("Error_AoA", "N/A")), str(client.get("X_RSSI", "N/A")),
                    str(client.get("Y_RSSI", "N/A")), str(client.get("Error_RSSI", "N/A")))
                    for j, client in enumerate(data)
                    if isinstance(client, dict)
                ]

                data_table = MDDataTable(
                    size_hint=(0.9, None),
                    pos_hint={'center_x': 0.5},
                    height=dp(300),  # ลดขนาดเพื่อให้ ScrollView ใช้งานได้ดีขึ้น
                    use_pagination=True,
                    check=True,
                    column_data=[
                        ("No.", dp(20)),
                        ("Point", dp(20)),
                        ("X_AoA", dp(20)),
                        ("Y_AoA", dp(20)),
                        ("Error_AoA", dp(20)),
                        ("X_RSSI", dp(30)),
                        ("Y_RSSI", dp(30)),
                        ("Error_RSSI", dp(30)),
                    ],
                    row_data=row_data,
                )

                layout.add_widget(data_table)

            scroll_view.add_widget(layout)  #add Layout to ScrollView
            main_layout.add_widget(scroll_view)  #add ScrollView in main Layout 

            self.clear_widgets()
            self.add_widget(main_layout)  #add main Layout to ClientsTable

    #add ClientsTable to ScreenManager
    sm.add_widget(ClientsTable(name='Clientstable'))
    sm.add_widget(MapScreen(name='map_screen'))


    class DeviceDispatcher(BluetoothDispatcher):
        def __init__(self, device, rssi, uuid, major, minor):
            super().__init__()
            self._device = device
            self._address: str = device.getAddress()
            self._name: str = device.getName() or ""
            self._rssi: int = rssi
            self._uuid: str = uuid  # Store the UUID
            self._major: str = major # Store the Major
            self._minor: str = minor # Store the Minor
        @property
        def title(self) -> str:
            return f"<{self._address}><{self._name}><{self._uuid}><{self._major}"

        def on_connection_state_change(self, status: int, state: int):
            if status == GATT_SUCCESS and state:
                Logger.info(f"Device: {self.title} connected")
            else:
                Logger.info(f"Device: {self.title} disconnected. {status=}, {state=}")
                # self.close_gatt()
                if status == 133:
                    # Retry connection after delay
                    Clock.schedule_once(lambda dt: self.reconnect(), 5)
                Logger.info(f"Scan <{self._name}> Complete")
                # Clock.schedule_once(callback=lambda dt: self.reconnect(), timeout=15)

        def on_rssi_updated(self, rssi: int, status: int):
            Logger.info(f"Device: {self.title} RSSI: {rssi}")
            # self.send_data_to_api(self._name, rssi)
            # Clock.schedule_once(lambda dt: self.update_ui(self._name, rssi), 0)  # Schedule UI update

        def periodically_update_rssi(self):
            """
            Clock callback to read
            the signal strength indicator for a connected device.
            """
            if self.gatt:  # if device is connected
                try:
                    self.update_rssi()
                except Exception as e:
                    Logger.error(f"Failed to update RSSI: {e}")

        def reconnect(self):
            Logger.info(f"Device: {self.title} try to reconnect ...")
            self.connect_gatt(self._device)

        def start(self):
            """Start connection to device."""
            
            if not self.gatt:
                self.connect_gatt(self._device)
            Clock.schedule_interval(callback=lambda dt: self.periodically_update_rssi(), timeout=5)
            
        def update_ui(self, name, rssi):
            scanned_info = f"{name}, RSSI: {rssi} dBm\n, UUID: {self._uuid}, Major: {self._major}, Minor: {self._minor}"
            app = App.get_running_app()
            current_text = app.root.ids.label.text
            # app.root.ids.label.text = current_text + scanned_info  # เพิ่มข้อมูลใหม่
        
    class ScannerDispatcher(BluetoothDispatcher):
        def __init__(self,target_filters=None):
            super().__init__()
            # Stores connected devices addresses
            self._devices = {}
            self.device = None
            self.target_filters = target_filters if target_filters is not None else []

        def on_scan_started(self, success: bool):
            Logger.info(f"Scan: started {'successfully' if success else 'unsuccessfully'}")
            if not success:
                # send to MyApp
                App.get_running_app().update_status("unsuccessful") 
            Logger.info("Not Sure:")
        def start_scan(self):
            # Start Scan Bluetooth Hear
            # Call the scan method from the parent class.
            super().start_scan()  
            
        def stop_scan(self):
            super().stop_scan()
            Logger.info("Stop: completed")

        def on_scan_completed(self):
            if self.device:
                self.connect_gatt(self.device)  # connect to device
                Logger.info("Scan: completed")
                # self.clear_devices()
                    
        def on_device(self, device, rssi, advertisement):
            address = device.getAddress()
            name = device.getName()
            data = advertisement.data
            parsed_data = list(advertisement.parse(data)) 
            uuid = None
            major = None
            minor = None
            
            for item in parsed_data:
                if item.ad_type == 9: #name
                    name = item.data.decode('utf-8')  # convert to string
                elif item.ad_type == 255:  #UUID
                    data_hex = item.data.hex()  #hex string
                    uuid_hex = data_hex[8:40]
                    uuid = uuid_hex

                    major_hex = data_hex[40:44] #2 bytes (4 digit)at 25-28
                    minor_hex = data_hex[44:48] #2 bytes (4 digit)at 29-32
                    #convert Major and Minor to base 10 or decimal
                    if major_hex and minor_hex:
                        major = int(major_hex, 16)
                        minor = int(minor_hex, 16)
            
            Logger.info(f"Discovered device with UUID: {uuid} and Major: {major}")        
            # if uuid in self.target_uuids:
            if any(filter.get("uuid") == uuid and filter.get("major") == major for filter in self.target_filters):
                Logger.info("found_data: completed")
                App.get_running_app().update_found_data(uuid, major, rssi)
            # if uuid and major in self.target_filters:
                if major not in self._devices:
                    # Create dispatcher instance for a new device
                    dispatcher = DeviceDispatcher(device, rssi, uuid, major, minor)
                    # Remember address,
                    # to avoid multiple dispatchers creation for this device
                    self._devices[address] = dispatcher
                    Logger.info(f"Scan: device <{name}> address <{address}> added with UUID <{uuid}> and Major <{major}>")
                    dispatcher.start()
                    
                self.device = device
                # self.stop_scan()  
                
            else:
                Logger.info(f"UUID {uuid} does not match target UUIDs.")
                return
                    
            #self.stop_scan()
            return name
        
        def clear_devices(self):
            self._devices.clear()  
    class MyApp(MDApp,BluetoothDispatcher):
        def build(self):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Amber"
            self.target_device_names = ["P2N_09725", "P2N_09714", "ZLB_39612","IPHONES"]
            self.scan_results = []
            self.x_real = None
            self.y_real = None
            self.point = None
            self.scanned_point = []
            self.scanned_point.append({"point": "F"})
            self.previous_point = self.point
            self.x_cal = 7.5
            self.y_cal = 0.0
            self.start = None
            self.status_aoa = None
            self.status_rssi = None
            self.dialog = None  #MDDialog For general notifications
            self.dialog_restart = None  #MDDialog For notification of restart
            
            #track found data
            self.target_data_set = [
                {"uuid": "d4444444444444444444444444444444", "major": 888},
                {"uuid": "d4444444444444444444444444444444", "major": 111},
                {"uuid": "c3333333333333333333333333333333", "major": 888},
                {"uuid": "c3333333333333333333333333333333", "major": 111},
                {"uuid": "b2222222222222222222222222222222", "major": 888},  # A3 HOR
                {"uuid": "b2222222222222222222222222222222", "major": 111},  # A3 VER
                {"uuid": "a1111111111111111111111111111111", "major": 888},  # A4 HOR
                {"uuid": "a1111111111111111111111111111111", "major": 111}   # A4 VER
            ]
            self.found_data = set()  
            self.screen = Builder.load_string(KV)
            
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
            return self.screen
            # return self.manager

        def switch_theme_style(self):
            self.theme_cls.primary_palette = (
                "Orange" if self.theme_cls.primary_palette == "Blue" else "Blue"
            )
            self.theme_cls.theme_style = (
                "Dark" if self.theme_cls.theme_style == "Light" else "Light"
            )
        def close_application(self):
            App.get_running_app().stop()
            
        #--------------------------------------------------------------------------
        #Get status from scanner
        def update_status(self, status):
            if status == "unsuccessful":
                self.root.ids.status.text = "Pls restart. Scan unsuccessfully"
                self.root.ids.status2.text = "Pls restart. Scan unsuccessfully"
                Clock.schedule_once(lambda dt: self.show_restart_alert())
                
        #Show notification of restart
        def show_restart_alert(self):
            Logger.info("restart_alert_occur")
        #     if not self.dialog_restart:  #if don't have Dialog. Create new
        #         self.dialog_restart = MDDialog(
        #             title="Scanning is Unsuccessfully!",
        #             text="Pls. Open app again",
        #             buttons=[
        #                 MDRaisedButton(
        #                     text="OK",
        #                     on_release=lambda x: self.close_app()
        #                 )
        #             ]
        #         )
        #         self.dialog_restart.open()  #Dialog Open

        #     elif not self.dialog_restart._is_open:  #if have Dialog but not open --> open
        #         self.dialog_restart.open()
                
        def close_app(self):
            if platform == "android":
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                PythonActivity.mActivity.finish()
            else:
                sys.exit()

        #Show notification from calculated
        def show_alert(self, message):
            if not self.dialog:
                self.dialog = MDDialog(
                    title="Calculate",
                    text=message,
                    buttons=[
                        MDRaisedButton(
                            text="OK",
                            on_release=lambda x: self.dialog.dismiss()
                        )
                    ]
                )
            else:
                self.dialog.text = message  #Change message according to the dialog.
            self.dialog.open()
            
        #--------------------------------------------------------------------------
        #Start Scan
        @property
        def service(self):
            return autoclass("test.able.scanservice.ServiceAble")

        @property
        def activity(self):
            return autoclass("org.kivy.android.PythonActivity").mActivity

        @require_bluetooth_enabled

        def start_service(self, loop_count=0):
            #Check if Bluetooth is enabled
            if not self.is_bluetooth_enabled():
                self.request_bluetooth_enable()
                return
                
            #if self.x_real is None or self.y_real is None:
                #self.show_alert("Please select a Point! before starting the scan")
                #return  #Stop if not select
            
            Logger.info(f"loop_count: {loop_count}")
                    
            self.service.start(self.activity, "")
            Logger.info("Service started.")

            #Call ScannerDispatcher for scan devices
            self.scanner_dispatcher = ScannerDispatcher(target_filters=self.target_data_set)
            Logger.info("Starting scan...")
            self.start = "start"

            self.root.ids.status.text = "Scanning..."
            self.root.ids.status2.text = "Scanning..."
            #Clear previous data before new scan
            self.root.ids.label.text = ""  
            self.root.ids.label_rssi_cal.text = ""
            self.root.ids.label_aoa_cal.text = ""
            self.root.ids.label_rssi_status.text = ""
            self.root.ids.label_aoa_status.text = ""
            
            #Start the scanning process
            self.scan_for_data()
        
        def scan_for_data(self):
            self.scanner_dispatcher.start_scan()
            Clock.schedule_once(self.check_results, 20)  #Schedule to check results after 20 seconds
        def check_results(self, dt):
            Logger.info(f"found_data first: {self.found_data}")
            self.scanner_dispatcher.stop_scan()
            found_data_filtered = {(d[0], d[1]) for d in self.found_data}
            #get uuid and major from target_data_set
            target_data_filtered = {(d['uuid'], d['major']) for d in self.target_data_set}
            if found_data_filtered == target_data_filtered:
                Logger.info("All target data found.")
                self.root.ids.status.text = "All target data found. Stopping scan."
                self.scanner_dispatcher.stop_scan()  #Stop scanning
                self.update_scan_results(self.found_data)
                
                #Set a flag to prevent re-scanning
                self.scanning = False
                self.stop_scan()
            else:
                Logger.info("Not all target data found. Stopping scan...")
                self.stop_scan()
            
        def check_scan_results(self, dt):
            self.scanner_dispatcher.stop_scan() #Stop scanning
            #print("found_data first:", self.found_data)
            Logger.info(f"found_data first: {self.found_data}")
            # print("target_data_set:", self.target_data_set)
            
            #get uuid and major from found_data
            found_data_filtered = {(d[0], d[1]) for d in self.found_data}
            #get uuid and major from target_data_set
            target_data_filtered = {(d['uuid'], d['major']) for d in self.target_data_set}
            
            #Check if we found all target data
            if found_data_filtered == target_data_filtered:
                Logger.info("All target data found.")
                self.root.ids.status.text = "All target data found. Stopping scan."
                self.scanner_dispatcher.stop_scan()  #Stop scanning
                self.update_scan_results(self.found_data)
                
                #Set a flag to prevent re-scanning
                self.scanning = False
                self.stop_scan()

            else:
                Logger.info("Not all target data found. Restarting scan...")
                self.stop_scan()
                self.scan_for_data()  #Scan again

        #Update from Scannerdispather
        def update_found_data(self, uuid, major, rssi):
            if rssi != 127: #127 is mean can't find the value
                
                #only check UUID and Major
                data_tuple = (uuid, major)
                
                # if data_tuple not in self.found_data:
                if data_tuple not in {(d[0], d[1]) for d in self.found_data}:
                    self.found_data.add((uuid, major, rssi))
                    Logger.info(f"Updated found data: {self.found_data}")

        def update_scan_results(self, found_data):
            Logger.info(f"All target data has been successfully collected")
            

            self.scan_results = list(self.found_data)
            if self.scan_results:
                self.display_scan_results()
                self.found_data.clear()
            self.root.ids.status.text = "Scan Complete"
            self.root.ids.status2.text = "Scan Complete"
            self.scanning = False
            
        #end of scan--------------------------------------------------------------------------
        
        #Screen 2 
        def open_menu_cal(self, caller_cal):
            self.menu_cal.caller = caller_cal
            self.menu_cal.open()
        def reset_menu_caller_cal(self):
            self.menu_cal.caller = self.root.ids.menu_button_cal
        #Screen 4
        def open_menu_map(self, caller_map):
            self.menu_map.caller = caller_map
            self.menu_map.open()
        def reset_menu_caller_map(self):
            self.menu_map.caller = self.root.ids.menu_button_map
        # def reset_menu_caller_map(self, caller_map):
        #     self.menu_map.caller = caller_map
        
        #call 'point' from database and show in screen
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
        #--------------------------------------------------------------------------
        
        #show point(A,B,C,D,E,F) of Screen 4 (table)
        def menu_callback_map(self, text_item):
            self.menu_map.dismiss()
            print(f"You selected point: {text_item}") 
            
            points_aoa = self.fetch_data_map_aoa(text_item)  #get all coordinates from API
            points_rssi = self.fetch_data_map_rssi(text_item)
            
            if points_aoa:
                if points_rssi:
                    length_aoa = len(points_aoa)
                    length_rssi = len(points_rssi)
                    
                    print(f"Found {length_aoa} points for {text_item}: {points_aoa}")
                    print(f"Found {length_rssi} points for {text_item}: {points_rssi}")
                    
                    Clock.schedule_once(lambda dt: self.plot_points(text_item, points_aoa, points_rssi), 0.1)
                    
                    #Update values ​​stored in class
                    self.points_data_aoa = {text_item: points_aoa}
                    self.points_data_rssi = {text_item: points_rssi}#keep all x, y in dict
                    
                    #Display only the first point retrieved
                    aoa_x, aoa_y = points_aoa[0] if points_aoa else (None, None)
                    rssi_x, rssi_y = points_rssi[0] if points_rssi else (None, None)
                    print(f"{text_item}: x = {aoa_x}, y = {aoa_y}")
                    print(f"{text_item}: x = {rssi_x}, y = {rssi_y}")
            else:
                print("Point not found in API response")
                print(f"{text_item}: No data found")
            
        #plot to map in Screen 4 (table)
        def plot_points(self, text_item, points_aoa, points_rssi):
            results_item = '\n'
            results_item += f"\n{text_item}"
            screen_manager = self.root.ids.get("screen_manager")  
            # print("screen_managerAfter:", screen_manager)

            if screen_manager:
                map_screen = screen_manager.get_screen("map_screen")
                map_point = map_screen.ids.get("map_point")
                label_point_map = map_screen.ids.get("label_point_map")

                if map_point:
                    #for point AoA 
                    for x_real, y_real in points_aoa:
                        x_pixel, y_pixel = self.calculate_real_to_pixel(x_real, y_real)
    
                        print(f"Real: ({x_real}, {y_real}) -> Pixel: ({x_pixel}, {y_pixel})")
                        map_point.plot_point_map_aoa(x_pixel, y_pixel, (x_real, y_real), text_item)
                        
                    #for point rssi
                    for x_real, y_real in points_rssi:
                        #in database position_rssi it have value --> can't calculate
                        if x_real != "can't calculate" and y_real != "can't calculate":
                            x_real = float(x_real) 
                            y_real = float(y_real)
                            x_pixel, y_pixel = self.calculate_real_to_pixel(x_real, y_real)

                            print(f"Real: ({x_real}, {y_real}) -> Pixel: ({x_pixel}, {y_pixel})")
                            map_point.plot_point_map_rssi(x_pixel, y_pixel, (x_real, y_real), text_item)
                            
                else:
                    print("map_point not found in map_screen")
                    
                if label_point_map:
                    label_point_map.text = results_item
                else:
                    print("label_point_map not found in map_screen")
            else:
                print("screen_manager not found in root.ids")
            
        #fetch_data from aoa and rssi
        def fetch_data_map_aoa(self, point):
            url = 'http://192.168.100.49:5000/Point_Map_aoa' #IP of server to connect database
            try:
                response = requests.get(url, json={"point": point})  #send JSON to API
                print("Response Text:", response.text)  
                
                if response.status_code == 200:
                    data = response.json()
                    # print("Data received:", data)
                    # Logger.info(f"Data is : {data}")
                    
                    #check API send data back is list or not
                    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                        return [(item.get("x", 0), item.get("y", 0)) for item in data]  #x, y 
                    else:
                        Logger.error("Invalid data format received")
                        return []
                else:
                    Logger.error(f"Failed with status code {response.status_code}")
            except Exception as e:
                Logger.error(f"Error fetching data: {e}")
            return []
        
        def fetch_data_map_rssi(self, point):
            url = 'http://192.168.100.49:5000/Point_Map_rssi' #IP of server to connect database
            try:
                response = requests.get(url, json={"point": point})  #send JSON to API
                print("Response Text:", response.text)  
                
                if response.status_code == 200:
                    data = response.json()
                    # print("Data received:", data)
                    # Logger.info(f"Data is : {data}")
                    
                    #check API send data back is list or not
                    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                        return [(item.get("x", 0), item.get("y", 0)) for item in data]  #x, y 
                    else:
                        Logger.error("Invalid data format received")
                        return []
                else:
                    Logger.error(f"Failed with status code {response.status_code}")
            except Exception as e:
                Logger.error(f"Error fetching data: {e}")
            return []
        #--------------------------------------------------------------------------
            
        #calculate real x,y to pixel x,y in screen
        def calculate_real_to_pixel(self, x_real, y_real):
            origin_x = 131 
            origin_y = 405 
            width = 776 
            height = 990 
            real_width = 14.924 
            real_height = 18.191
            
            scale_x = width / real_width  # Horizontal pixel/meter ratio
            scale_y = height / real_height  # Vertical pixel/meter ratio

            #Convert real coordinates to pixel coordinates
            x_pixel = origin_x + (x_real * (scale_x))
            y_pixel = origin_y + (y_real * (scale_y))
            return x_pixel, y_pixel
        
        #called from Screen3 (map)
        def plot_initial_point(self):
            x_cal = self.x_cal
            y_cal = self.y_cal
            real_coordinate = (x_cal, y_cal)
            map_coordinate = self.calculate_real_to_pixel(*real_coordinate)    

            # plot x,y
            map_widget = self.root.ids.map_widget
            map_widget.plot_point(*map_coordinate, real_coordinate) 
        #--------------------------------------------------------------------------

        #show on screen
        def display_scan_results(self):
            self.scanned_devices = []
            
            scanned_info = ''
            A1_V, A1_H, A2_V, A2_H = 0, 0 ,0 ,0
            A3_V, A3_H, A4_V, A4_H = 0 ,0 ,0 ,0
            for uuid, major, rssi in self.scan_results:
                # Logger.info(f"Result: devices: {device}")
                # name = device._name
                # uuid = device.uuid
                # major = device.major
                # minor = device._minor
                #265	78	A1_V	-73	2025-02-25 16:25:58
                if uuid == None:
                    scanned_info = f"Don't have any Device is Match"
                else:
                    if ((uuid == "a1111111111111111111111111111111") & (major == 111)):
                        name = "A1(VER)"
                        anchor_id = "A1_V"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A1_V = rssi
                        
                    elif ((uuid == "a1111111111111111111111111111111") & (major == 888)):
                        name = "A1(HOR)"
                        anchor_id = "A1_H"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A1_H = rssi
                        
                        
                    elif ((uuid == "b2222222222222222222222222222222") & (major == 111)):
                        name = "A2(VER)"
                        anchor_id = "A2_V"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A2_V = rssi
                        
                    elif ((uuid == "b2222222222222222222222222222222") & (major == 888)):
                        name = "A2(HOR)"
                        anchor_id = "A2_H"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A2_H = rssi
                        

                    ######################## เพิ่ม A3,A4 ###########################
                    elif ((uuid == "c3333333333333333333333333333333") & (major == 111)):  # ใส่ UUID ของ A3
                        name = "A3(VER)"
                        anchor_id = "A3_V"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A3_V = rssi
                    elif ((uuid == "c3333333333333333333333333333333") & (major == 888)):  # ใส่ UUID ของ A3
                        name = "A3(HOR)"
                        anchor_id = "A3_H"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A3_H = rssi
                    elif ((uuid == "d4444444444444444444444444444444") & (major == 111)):  # ใส่ UUID ของ A4
                        name = "A4(VER)"
                        anchor_id = "A4_V"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A4_V = rssi
                    elif ((uuid == "d4444444444444444444444444444444") & (major == 888)):  # ใส่ UUID ของ A4
                        name = "A4(HOR)"
                        anchor_id = "A4_H"
                        scanned_info += f"{name}, RSSI: {rssi} dBm\n"
                        A4_H = rssi
                        
                    else:
                        name = "5"
                        anchor_id = "UNKNOWN"
                        scanned_info += f"A: {name}, RSSI: {rssi} dBm,\n Major: {major}\n"
                        A1_V = A1_H = A2_V = A2_H = A3_V = A3_H = A4_V = A4_H = rssi
                    
                
                self.scanned_devices.append({"rssi": rssi, "anchor_id": anchor_id})
                
            #all are found then calculated
            # x1, y1 = self.process_data_aoa_rssi(A1_V, A1_H, A2_V, A2_H, A3_V, A3_H, A4_V, A4_H)
            # x2, y2 = self.process_rssi(A1_V, A1_H, A2_V, A2_H, A3_V, A3_H, A4_V, A4_H)
            # self.results_status(x1, y1, x2, y2)
            # self.x_cal = x1
            # self.y_cal = y1
            
            # scanned_info += f"positions(AoA): ({x1:.2f}, {y1:.2f})\n"
            # scanned_info3 = f"({x1:.2f}, {y1:.2f})\n"
            # if x2 is not (-1) and y2 is not (-1):
            #     scanned_info += f"positions(rssi): ({x2:.2f}, {y2:.2f})\n"
            #     scanned_info4 = f"({x2:.2f}, {y2:.2f})\n"
            # else:
            #     scanned_info += f"positions(rssi): x,y error\n"
            #     scanned_info4 = f"x,y error\n"
                
            self.root.ids.label.text = scanned_info
            # self.root.ids.label_aoa_cal.text = scanned_info3
            # self.root.ids.label_rssi_cal.text = scanned_info4
            # Logger.info('Bluetooth: ' + '\n' + scanned_info)
            # return x1, y1
        #--------------------------------------------------------------------------
        
        #function calculate status of point
        def results_status(self, x1, y1, x2, y2):
            self.scanned_aoa_cal_point = []
            self.scanned_rssi_cal_point = []
            self.scanned_point = []
            
            #Use values in class variables
            if self.x_real is not None and self.y_real is not None and self.point is not None:
                x_aoa_cal = x1
                y_aoa_cal = y1
                x_rssi_cal = x2
                y_rssi_cal = y2
                #self.scanned_point.append({"point": self.point})
                self.previous_point = self.point
                self.distance_aoa = None
                self.distance_rssi = None

                #Calculate the distance between points
                x_aoa_cal = round(x_aoa_cal, 2)
                y_aoa_cal = round(y_aoa_cal, 2)
                self.distance_aoa = round(math.sqrt((x_aoa_cal - self.x_real) ** 2 + (y_aoa_cal - self.y_real) ** 2), 2)
                
                if  x_rssi_cal != (-1) and y_rssi_cal != (-1): #ckeck if can't calculate
                    x_rssi_cal = round(x_rssi_cal, 2)
                    y_rssi_cal = round(y_rssi_cal, 2)
                    self.distance_rssi = round(math.sqrt((x_rssi_cal - self.x_real) ** 2 + (y_rssi_cal - self.y_real) ** 2), 2)
                else:
                    self.distance_rssi = "can't calculate"

                #Check the distance / show status / keep value for send data
                #Calculated <= 5 meters
                if abs(self.distance_aoa) <= 5:
                    print("AoA is Success!")
                    self.status_aoa = "Success"
                    self.root.ids.label_aoa_status.text = f"{self.status_aoa}\n(error {self.distance_aoa}) m"
                    self.scanned_aoa_cal_point.append({"x": x_aoa_cal, "y": y_aoa_cal, "error": self.distance_aoa, "status": self.status_aoa, "point": self.point})
                    
                    if self.distance_rssi != "can't calculate":
                        if abs(self.distance_rssi) <= 5:
                            print("RSSi is Success!")
                            self.status_rssi = "Success"
                            self.root.ids.label_rssi_status.text = f"{self.status_rssi}\n(error {self.distance_rssi} m)"
                            self.scanned_rssi_cal_point.append({"x": x_rssi_cal, "y": y_rssi_cal, "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                            self.show_alert(f"You have arrived point {self.point}! \n(Both AoA and RSSI)")  # ใส่ค่า point ในข้อความ
                            
                        elif abs(self.distance_rssi) > 5:
                            print("RSSI is Unsuccess: Distance =", self.distance_rssi)
                            self.status_rssi = "Unsuccess"
                            self.root.ids.label_rssi_status.text = f"{self.status_rssi}\n(error {self.distance_rssi} m)"
                            self.scanned_rssi_cal_point.append({"x": x_rssi_cal, "y": y_rssi_cal, "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                            self.show_alert(f"You have arrived point {self.point}! \n(in AoA calculated)")  
                    else:
                        print("RSSi can't calculate")
                        self.status_rssi = "x,y error"
                        self.root.ids.label_rssi_status.text = f"{self.status_rssi}"
                        self.scanned_rssi_cal_point.append({"x": "can't calculate", "y": "can't calculate", "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                        self.show_alert(f"You have arrived point {self.point}! \n(in AoA calculated)") 
                        
                elif (abs(self.distance_aoa) > 5):
                    print("AoA is Unsuccess: Distance =", self.distance_aoa)
                    self.status_aoa = "Unsuccess"
                    self.root.ids.label_aoa_status.text = f"{self.status_aoa}\n(error {self.distance_aoa} m)"
                    self.scanned_aoa_cal_point.append({"x": x_aoa_cal, "y": y_aoa_cal, "error": self.distance_aoa, "status": self.status_aoa, "point": self.point})
                    
                    if self.distance_rssi != "can't calculate":
                        if abs(self.distance_rssi) <= 5:
                            print("RSSi is Success!")
                            self.status_rssi = "Success"
                            self.root.ids.label_rssi_status.text = f"{self.status_rssi}\n(error {self.distance_rssi} m)"
                            self.scanned_rssi_cal_point.append({"x": x_rssi_cal, "y": y_rssi_cal, "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                            self.show_alert(f"You have arrived point {self.point}! \n(in RSSI calculated)")
                            
                        elif abs(self.distance_rssi) > 5:
                            print("RSSI is Unsuccess: Distance =", self.distance_rssi)
                            self.status_rssi = "Unsuccess"
                            self.root.ids.label_rssi_status.text = f"{self.status_rssi}\n(error {self.distance_rssi} m)"
                            self.scanned_rssi_cal_point.append({"x": x_rssi_cal, "y": y_rssi_cal, "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                            self.show_alert(f"You have not arrived point {self.point}! (distance aoa : {self.distance_aoa:.2f} m)\n(distance rssi : {self.distance_rssi:.2f} m)")
                    else:
                        print("RSSi can't calculate")
                        self.status_rssi = "x,y error"
                        self.root.ids.label_rssi_status.text = f"{self.status_rssi}"
                        self.scanned_rssi_cal_point.append({"x": "can't calculate", "y": "can't calculate", "error": self.distance_rssi, "status": self.status_rssi, "point": self.point})
                        self.show_alert(f"You have not arrived point {self.point}! (distance aoa : {self.distance_aoa:.2f} m)")
                        
            else:
                print("No coordinates available yet.")
        #--------------------------------------------------------------------------
        
        #change status before send to database
        def toggle_edit_status(self, button_instance):
            if self.x_real is None or self.y_real is None:
                self.show_alert("Please select a Point! before edit status")
                return  #Stop if not select
            elif self.start is None:
                self.show_alert("Please start scan! before edit status")
                return  #Stop if not start
            elif self.status_aoa is None or self.status_rssi is None:
                self.show_alert("scanning..., please wait a moment)")
                return  #Stop if scanning
            
            #pull distance
            distance_aoa = self.distance_aoa
            distance_rssi = self.distance_rssi

            #function change status
            def change_status(selected_id):

                if selected_id == "aoa":
                    if "Success" in self.status_aoa:
                        self.status_aoa = "Unsuccess"
                    elif "Unsuccess" in self.status_aoa:
                        self.status_aoa = "x,y error"
                    else:
                        self.status_aoa = "Success"

                    #update status on screen(aoa)
                    if self.status_aoa != "x,y error":
                        self.root.ids.label_aoa_status.text = f"{self.status_aoa}\n(error {distance_aoa} m)"
                    else:
                        self.root.ids.label_aoa_status.text = f"{self.status_aoa}"
                    
                    #update status in scanned_aoa_cal_point before send to database
                    for item in self.scanned_aoa_cal_point:
                        if item["point"] == self.point:
                            item["status"] = self.status_aoa

                elif selected_id == "rssi":
                    if "Success" in self.status_rssi:
                        self.status_rssi = "Unsuccess"
                    elif "Unsuccess" in self.status_rssi:
                        self.status_rssi = "x,y error"
                    else:
                        self.status_rssi = "Success"

                    #update status on screen(rssi)
                    if self.status_rssi != "x,y error":
                        self.root.ids.label_rssi_status.text = f"{self.status_rssi}\n(error {distance_rssi} m)"
                    else:
                        self.root.ids.label_rssi_status.text = f"{self.status_rssi}"

                    #update status in scanned_rssi_cal_point before send to database
                    for item in self.scanned_rssi_cal_point:
                        if item["point"] == self.point:
                            item["status"] = self.status_rssi

                self.menu.dismiss()  # close Dropdown Menu

            menu_items = [
                {"text": "AoA", "on_release": lambda: change_status("aoa")},
                {"text": "RSSI", "on_release": lambda: change_status("rssi")},
            ]

            #create Dropdown Menu
            self.menu = MDDropdownMenu(
                caller=button_instance,
                items=menu_items,
                width_mult=4
            )
            self.menu.open()
        #-------------------------------------------------------------------------------------------------
        
        #load data to class Clientstable    
        def load_data(self):
            try:
                screen = self.root.ids.screen_manager.get_screen('Clientstable')
                wait_lbl = self.root.ids.wait_label
                load_btn = self.root.ids.load_data_btn

                #show message "wait a minute!" and hide the Load Data button
                wait_lbl.text = "wait a minute....."
                wait_lbl.opacity = 1
                load_btn.disabled = True
                load_btn.opacity = 0

                #wait 0.1 s before starting to load data
                Clock.schedule_once(lambda dt: self.load_table(screen), 0.1)
                Logger.info("Data loading started")

            except Exception as e:
                Logger.error(f"Error loading data: {e}")

        def load_table(self, screen):
            #call function load_table
            screen.load_table()

            #use Clock.schedule_once to hide message "wait a minute!" and button Load Data
            Clock.schedule_once(lambda dt: self.hide_wait_label(), 3)

        def hide_wait_label(self):
            #hide message "wait a minute!" and button Load Data
            wait_lbl = self.root.ids.wait_label
            load_btn = self.root.ids.load_data_btn
            text_lbl1 = self.root.ids.text1
            text_lbl2 = self.root.ids.text2
            
            wait_lbl.text = ""
            wait_lbl.opacity = 0
            text_lbl1.opacity = 0
            text_lbl2.opacity = 0
            load_btn.disabled = False
            load_btn.opacity = 0
        #--------------------------------------------------------------------------
        
        #send all data to database    
        def send_data(self):
            #if self.x_real is None or self.y_real is None:
                #self.show_alert("Please select a Point! Don't have a data to send")
                #return  #Stop if not select
            if self.start is None:
                self.show_alert("Please start scan! Don't have a data to send")
                return  #Stop if not select
            # elif self.status_aoa is None or self.status_rssi is None:
            #     self.show_alert("scanning..., please wait a moment)")
            #     return  #Stop if not select
            
            url = "http://192.168.100.196:5000/rssi_data" #IP of server to connect database
            for device in self.scanned_point:
                data = {
                    "point": device['point']
                }
                try:
                    response = requests.post(url, json=data)
                    response.raise_for_status()
                    Logger.info(f'Successfully sent data to API: {response.json()}')
                except requests.exceptions.HTTPError as http_err:
                    Logger.error(f'HTTP error occurred: {http_err}')
                except Exception as err:
                    Logger.error(f'Other error occurred: {err}')
                    
            url_datalist = "http://192.168.100.196:5000/rssi_data_list" #IP of server to connect database
            for device in self.scanned_devices:
                data = {
                    "rssi": device.get('rssi'),  # ใช้ .get() เพื่อหลีกเลี่ยง KeyError
                    "anchor_id": device['anchor_id']
                    
                }
                try:
                    response = requests.post(url_datalist, json=data)
                    response.raise_for_status()
                    Logger.info(f'Successfully sent data to API: {response.json()}')
                except requests.exceptions.HTTPError as http_err:
                    Logger.error(f'HTTP error occurred: {http_err}')
                except Exception as err:
                    Logger.error(f'Other error occurred: {err}')
            
            '''url2 = "http://192.168.100.196:5000/position_aoa" #IP of server to connect database
            for device in self.scanned_aoa_cal_point:
                data = {
                    "x": device.get('x'),
                    "y": device.get('y'),  
                    "error": device.get('error'),
                    "status": device['status']
                }
                try:
                    response = requests.post(url2, json=data)
                    response.raise_for_status()
                    Logger.info(f'Successfully sent data to API(AoA): {response.json()}')
                except requests.exceptions.HTTPError as http_err:
                    Logger.error(f'HTTP error occurred(AoA): {http_err}')
                except Exception as err:
                    Logger.error(f'Other error occurred(AoA): {err}')
                    
            url3 = "http://192.168.100.151:5000/position_rssi" #IP of server to connect database
            for device in self.scanned_rssi_cal_point:
                data = {
                    "x": device.get('x'),
                    "y": device.get('y'),  
                    "error": device.get('error'),
                    "status": device['status']
                }
                try:
                    response = requests.post(url3, json=data)
                    response.raise_for_status()
                    Logger.info(f'Successfully rssi sent data to API(RSSI): {response.json()}')
                except requests.exceptions.HTTPError as http_err:
                    Logger.error(f'HTTP error occurred(RSSI): {http_err}')
                except Exception as err:
                    Logger.error(f'Other error occurred(RSSI): {err}')'''

            self.root.ids.status.text = "Data Sent"
            self.root.ids.status2.text = "Data Sent"
        #--------------------------------------------------------------------------

        #for stop scan
        def stop_service(self):
            if self.x_real is None or self.y_real is None:
                self.show_alert("Please select a Point! There is no data to stop")
                return  #Stop if not select
            elif self.start is None:
                self.show_alert("Please start scan! There is no data to stop")
                return  #Stop if not start
            
            self.scanning = False
            self.service.stop(self.activity)
            Logger.info("Scan: Stop Scanning")
            self.stop_scan()
            self.root.ids.status.text = "Stop Scanning"
            self.root.ids.status2.text = "Stop Scanning"
        
        def stop_scan(self):
            self.is_scanning = False #Set the status back to no scanning
            self.scanner_dispatcher.stop_scan()
            Logger.info("Scan stopped. Ready to start new scan.")
        #--------------------------------------------------------------------------
            
        def is_bluetooth_enabled(self):
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            return adapter.isEnabled()
        def request_bluetooth_enable(self):
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            intent = Intent(Settings.ACTION_BLUETOOTH_SETTINGS)
            activity.startActivity(intent)
            
        #--------------------------------------------------------------------------
        #AoA calculation algorithm
        def process_data_aoa_rssi(self, A1_V, A1_H, A2_V, A2_H, A3_V, A3_H, A4_V, A4_H):
            
            #find file Excel in folder assets
            file_path_1 = resource_find("assets/quadratic_horizontal.xlsx")
            file_path_2 = resource_find("assets/linear_horizontal.xlsx")
            
            #Check if the file actually exists
            if file_path_1 and file_path_2:
                print(f"File 1 Path: {file_path_1}")
                print(f"File 2 Path: {file_path_2}")
                Logger.info("Excel files processed successfully!")
            else:
                Logger.error("1:One or both Excel files are missing in the assets folder.")
            
            '''
            data_QLH = data_QLV = data_QRH = data_QRV = data_LL = data_LR = None
            data_QLH = pd.read_excel(file_path_1, sheet_name='QLH', engine='openpyxl')
            data_QLV = pd.read_excel(file_path_1, sheet_name='QLH', engine='openpyxl')
            data_QRH = pd.read_excel(file_path_1, sheet_name='QRH', engine='openpyxl')
            data_QRV = pd.read_excel(file_path_1, sheet_name='QRH', engine='openpyxl')

            data_LL = pd.read_excel(file_path_2, sheet_name='LL', engine='openpyxl')
            data_LR = pd.read_excel(file_path_2, sheet_name='LR', engine='openpyxl')
            '''
            #Show some data
            if data_QLH is not None:
                print(data_QLH.head())
            else:
                print("Can't Download data from file Excel")
        
            # get data from row 1 onwards (index 0 onwards)
            # use iloc[0:] for start row index 0 (row 1)
            rows_from_QLH_onward = data_QLH.iloc[0:]
            rows_from_QLV_onward = data_QLV.iloc[0:]
            rows_from_QRH_onward = data_QRH.iloc[0:]
            rows_from_QRV_onward = data_QRV.iloc[0:]

            rows_from_LL_onward = data_LL.iloc[0:]
            rows_from_LR_onward = data_LR.iloc[0:]

            rssi_hor_1 = A1_H # Hor_1
            rssi_ver_1 = A1_V # Ver_1
            rssi_hor_2 = A2_H # Hor_2
            rssi_ver_2 = A2_V # Ver_2
            
            ##############เพิ่มขึ้นมา 1 ตัวนะครับ จะได้ 4 ตัวครับ
            rssi_hor_3 = A3_H # Hor_1
            rssi_ver_3 = A3_V # Ver_1
            rssi_hor_4 = A4_H # Hor_1
            rssi_ver_4 = A4_V # Ver_1
                ############################################
            result_alpha = []
            result_beta = []
            result_pair_alpha_beta = []
            result_theta_alpha_beta = []

            result_phi = []
            result_delta = []
            result_pair_phi_delta = []
            result_theta_phi_delta = []

            result_distances = []

            # Anchor 1
            # calculatate "alpha"
            # Store the alpha value in the result_alpha array
            
            for index1, row in rows_from_QLH_onward.iterrows():
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant1 = (b**2) - (4 * a * (c - rssi_hor_1))
                # distance = row['distance']
                # print(f"a: {a:.6f}")
                # print(f"b: {b:.6f}")
                # print(f"c: {c:.6f}\n")

                alpha1 = alpha2 = float('nan')
                if discriminant1 >= 0:
                    alpha1 = ((-b) + math.sqrt(discriminant1)) / (2 * a)
                    alpha2 = ((-b) - math.sqrt(discriminant1)) / (2 * a)
                else:
                    alpha1 = alpha2 = float('nan')
                    
                result_alpha.append((alpha1, alpha2))
            # print(result_alpha)

            # calculate "beta" in the row matching alpha
            # Take the theta value and pair(alpha, beta) in array --> result_theta_alpha_beta and result_pair_alpha_beta respectively
            for index2, row in rows_from_QLV_onward.iterrows():
                if index2 >= len(result_alpha):  #If the number of beta rows is greater than alpha, stop
                    break
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant2 = (b**2) - (4 * a * (c - rssi_ver_1))

                beta1 = beta2 = float('nan')
                if discriminant2 >= 0:
                    beta1 = ((-b) + math.sqrt(discriminant2)) / (2 * a)
                    beta2 = ((-b) - math.sqrt(discriminant2)) / (2 * a)
                else:
                    beta1 = beta2 = float('nan')
                
                # matching 'alpha' and 'beta' at the same index
                alpha1, alpha2 = result_alpha[index2]
                distance = row['distance']
                pairs = [
                    [alpha1, (90 - beta1)],
                    [alpha1, (90 - beta2)],
                    [alpha2, (90 - beta1)],
                    [alpha2, (90 - beta2)]
                ]

                # keep pair(alpha, beta) and calculate theta
                for pair in pairs:
                    alpha, beta = pair
                    # check if alpha < 0 or beta > 90, theta is null
                    if (alpha >= 0 and beta <= 90):
                        theta = alpha + beta
                    else:
                        theta = float('nan')
                    
                    result_pair_alpha_beta.append(pair)
                    result_theta_alpha_beta.append(theta)
                result_distances.extend([distance] * 4)
            # print(result_pair_alpha_beta)

            # Anchor 2
            # calculate "phi"
            # Store the phi value in the result_phi array 
            for index1, row in rows_from_QRH_onward.iterrows():
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant1 = (b**2) - (4 * a * (c - rssi_hor_2))
                distance = row['distance']

                phi1 = phi2 = float('nan')
                if discriminant1 >= 0:
                    phi1 = ((-b) + math.sqrt(discriminant1)) / (2 * a)
                    phi2 = ((-b) - math.sqrt(discriminant1)) / (2 * a)
                else:
                    phi1 = phi2 = float('nan')
                    
                result_phi.append((phi1, phi2))
            # print(result_phi)

            # calculate "delta" in the row matching phi
            # Take the theta value and pair(phi, delta) in array --> result_theta_phi_delta and result_pair_phi_delta respectively
            for index2, row in rows_from_QRV_onward.iterrows():
                if index2 >= len(result_phi):  #If the number of delta rows is greater than phi, stop
                    break

                a = row['a']
                b = row['b']
                c = row['c']
                discriminant2 = (b**2) - (4 * a * (c - rssi_ver_2))

                delta1 = delta2 = float('nan')
                if discriminant2 >= 0:
                    delta1 = ((-b) + math.sqrt(discriminant2)) / (2 * a)
                    delta2 = ((-b) - math.sqrt(discriminant2)) / (2 * a)
                else:
                    delta1 = delta2 = float('nan')
                
                # matching 'phi' and 'delta' at the same index
                phi1, phi2 = result_phi[index2]
                distance = row['distance']
                pairs = [
                    [phi1, (90 - delta1)],
                    [phi1, (90 - delta2)],
                    [phi2, (90 - delta1)],
                    [phi2, (90 - delta2)]
                ]

                # keep pair(phi, delta) and calculate theta
                for pair in pairs:
                    phi, delta = pair
                    # check if phi < 0 or delta > 90, theta is null
                    if (phi >= 0 and delta <= 90):
                        theta = phi + delta
                    else:
                        theta = float('nan')
                    
                    result_pair_phi_delta.append(pair)
                    result_theta_phi_delta.append(theta)
                result_distances.extend([distance] * 4)

#################################เพิ่ม เพื่อคำนวณระยะทางที่ถูกต้องที่สุด##########################################################
                # Anchor 3
            # calculatate "alpha"
            # Store the alpha value in the result_alpha array
            
            for index1, row in rows_from_QLH_onward.iterrows():
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant1 = (b**2) - (4 * a * (c - rssi_hor_3))
                # distance = row['distance']
                # print(f"a: {a:.6f}")
                # print(f"b: {b:.6f}")
                # print(f"c: {c:.6f}\n")

                alpha1 = alpha2 = float('nan')
                if discriminant1 >= 0:
                    alpha1 = ((-b) + math.sqrt(discriminant1)) / (2 * a)
                    alpha2 = ((-b) - math.sqrt(discriminant1)) / (2 * a)
                else:
                    alpha1 = alpha2 = float('nan')
                    
                result_alpha.append((alpha1, alpha2))
            # print(result_alpha)

            # calculate "beta" in the row matching alpha
            # Take the theta value and pair(alpha, beta) in array --> result_theta_alpha_beta and result_pair_alpha_beta respectively
            for index2, row in rows_from_QLV_onward.iterrows():
                if index2 >= len(result_alpha):  #If the number of beta rows is greater than alpha, stop
                    break
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant2 = (b**2) - (4 * a * (c - rssi_ver_3))

                beta1 = beta2 = float('nan')
                if discriminant2 >= 0:
                    beta1 = ((-b) + math.sqrt(discriminant2)) / (2 * a)
                    beta2 = ((-b) - math.sqrt(discriminant2)) / (2 * a)
                else:
                    beta1 = beta2 = float('nan')
                
                # matching 'alpha' and 'beta' at the same index
                alpha1, alpha2 = result_alpha[index2]
                distance = row['distance']
                pairs = [
                    [alpha1, (90 - beta1)],
                    [alpha1, (90 - beta2)],
                    [alpha2, (90 - beta1)],
                    [alpha2, (90 - beta2)]
                ]

                # keep pair(alpha, beta) and calculate theta
                for pair in pairs:
                    alpha, beta = pair
                    # check if alpha < 0 or beta > 90, theta is null
                    if (alpha >= 0 and beta <= 90):
                        theta = alpha + beta
                    else:
                        theta = float('nan')
                    
                    result_pair_alpha_beta.append(pair)
                    result_theta_alpha_beta.append(theta)
                result_distances.extend([distance] * 4)
            # print(result_pair_alpha_beta)


            # Anchor 4
            # calculatate "alpha"
            # Store the alpha value in the result_alpha array
            
            for index1, row in rows_from_QLH_onward.iterrows():
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant1 = (b**2) - (4 * a * (c - rssi_hor_4))
                # distance = row['distance']
                # print(f"a: {a:.6f}")
                # print(f"b: {b:.6f}")
                # print(f"c: {c:.6f}\n")

                alpha1 = alpha2 = float('nan')
                if discriminant1 >= 0:
                    alpha1 = ((-b) + math.sqrt(discriminant1)) / (2 * a)
                    alpha2 = ((-b) - math.sqrt(discriminant1)) / (2 * a)
                else:
                    alpha1 = alpha2 = float('nan')
                    
                result_alpha.append((alpha1, alpha2))
            # print(result_alpha)

            # calculate "beta" in the row matching alpha
            # Take the theta value and pair(alpha, beta) in array --> result_theta_alpha_beta and result_pair_alpha_beta respectively
            for index2, row in rows_from_QLV_onward.iterrows():
                if index2 >= len(result_alpha):  #If the number of beta rows is greater than alpha, stop
                    break
                a = row['a']
                b = row['b']
                c = row['c']
                discriminant2 = (b**2) - (4 * a * (c - rssi_ver_4))

                beta1 = beta2 = float('nan')
                if discriminant2 >= 0:
                    beta1 = ((-b) + math.sqrt(discriminant2)) / (2 * a)
                    beta2 = ((-b) - math.sqrt(discriminant2)) / (2 * a)
                else:
                    beta1 = beta2 = float('nan')
                
                # matching 'alpha' and 'beta' at the same index
                alpha1, alpha2 = result_alpha[index2]
                distance = row['distance']
                pairs = [
                    [alpha1, (90 - beta1)],
                    [alpha1, (90 - beta2)],
                    [alpha2, (90 - beta1)],
                    [alpha2, (90 - beta2)]
                ]

                # keep pair(alpha, beta) and calculate theta
                for pair in pairs:
                    alpha, beta = pair
                    # check if alpha < 0 or beta > 90, theta is null
                    if (alpha >= 0 and beta <= 90):
                        theta = alpha + beta
                    else:
                        theta = float('nan')
                    
                    result_pair_alpha_beta.append(pair)
                    result_theta_alpha_beta.append(theta)
                result_distances.extend([distance] * 4)
            # print(result_pair_alpha_beta)
############################################################################################



            # function for find "theta" value close to 90
            # Anchor1
            def find_closest_to_ninety_anchor1(theta_values, pairs, row_indices, data_frame):
                closest_value = None
                closest_diff = float('inf')
                closest_pair = None
                closest_row_index = None
                closest_distance = None
                
                distances = [i * 0.5 for i in range(1, 31)]  # สร้างค่า 0.5 ถึง 22.5 (45 ค่า)
                distances = [d for d in distances for _ in range(4)]  # ทำให้แต่ละค่าเกิด 4 ครั้ง
                # print(distances)

                for theta, pair, row_index in zip(theta_values, pairs, row_indices):
                    if isinstance(theta, float):
                        diff = abs(90 - theta)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_value = theta
                            closest_pair = pair
                            closest_row_index = row_index
                            # ตั้งค่า closest_distance ตามค่าในรายการ distances
                            closest_distance = distances[row_index] if row_index < len(distances) else None
                            # print(f"Found theta: {theta}, closest distance: {closest_distance}, from index: {row_index}")
                return closest_value, closest_pair, closest_row_index, closest_distance

            #Anchor2
            def find_closest_to_ninety_anchor2(theta_values, pairs, row_indices, data_frame):
                closest_value = None
                closest_diff = float('inf')
                closest_pair = None
                closest_row_index = None
                closest_distance = None
                
                # สร้างรายการ distance ตั้งแต่ 0.5 ถึง 22.5 อย่างละ 4 ครั้ง
                distances = [i * 0.5 for i in range(1, 34)]  # สร้างค่า 0.5 ถึง 22 (44 ค่า)
                distances = [d for d in distances for _ in range(4)]  # ทำให้แต่ละค่าเกิด 4 ครั้ง
                # print(distances)

                for theta, pair, row_index in zip(theta_values, pairs, row_indices):
                    if isinstance(theta, float):
                        diff = abs(90 - theta)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_value = theta
                            closest_pair = pair
                            closest_row_index = row_index
                            # ตั้งค่า closest_distance ตามค่าในรายการ distances
                            closest_distance = distances[row_index] if row_index < len(distances) else None
                            # print(f"Found theta: {theta}, closest distance: {closest_distance}, from index: {row_index}")
                return closest_value, closest_pair, closest_row_index, closest_distance

######################################################เพิ่ม ตรงนี้######################################################
            # Anchor3
            def find_closest_to_ninety_anchor3(theta_values, pairs, row_indices, data_frame):
                closest_value = None
                closest_diff = float('inf')
                closest_pair = None
                closest_row_index = None
                closest_distance = None
                
                distances = [i * 0.5 for i in range(1, 31)]  # สร้างค่า 0.5 ถึง 22.5 (45 ค่า)
                distances = [d for d in distances for _ in range(4)]  # ทำให้แต่ละค่าเกิด 4 ครั้ง
                # print(distances)

                for theta, pair, row_index in zip(theta_values, pairs, row_indices):
                    if isinstance(theta, float):
                        diff = abs(90 - theta)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_value = theta
                            closest_pair = pair
                            closest_row_index = row_index
                            # ตั้งค่า closest_distance ตามค่าในรายการ distances
                            closest_distance = distances[row_index] if row_index < len(distances) else None
                            # print(f"Found theta: {theta}, closest distance: {closest_distance}, from index: {row_index}")
                return closest_value, closest_pair, closest_row_index, closest_distance

            # Anchor4
            def find_closest_to_ninety_anchor4(theta_values, pairs, row_indices, data_frame):
                closest_value = None
                closest_diff = float('inf')
                closest_pair = None
                closest_row_index = None
                closest_distance = None
                
                distances = [i * 0.5 for i in range(1, 31)]  # สร้างค่า 0.5 ถึง 22.5 (45 ค่า)
                distances = [d for d in distances for _ in range(4)]  # ทำให้แต่ละค่าเกิด 4 ครั้ง
                # print(distances)

                for theta, pair, row_index in zip(theta_values, pairs, row_indices):
                    if isinstance(theta, float):
                        diff = abs(90 - theta)
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_value = theta
                            closest_pair = pair
                            closest_row_index = row_index
                            # ตั้งค่า closest_distance ตามค่าในรายการ distances
                            closest_distance = distances[row_index] if row_index < len(distances) else None
                            # print(f"Found theta: {theta}, closest distance: {closest_distance}, from index: {row_index}")
                return closest_value, closest_pair, closest_row_index, closest_distance
########################################################################################################


            # ค้นหาค่าที่ใกล้ 90 ที่สุดในผลลัพธ์ theta
            # สร้างตัวแปรเป็นอาเรย์เพื่อเก็บค่า
            closest_to_ninety_anchor1 = None
            closest_pair_to_ninety_anchor1 = None
            closest_distance_anchor1 = None

            closest_to_ninety_anchor2 = None
            closest_pair_to_ninety_anchor2 = None
            closest_distance_anchor2 = None
            
            ###############เพิ่มเพิ่มสำหรับ Anchor3 และ Anchor4#########
            closest_to_ninety_anchor3 = None
            closest_pair_to_ninety_anchor3 = None
            closest_distance_anchor3 = None

            closest_to_ninety_anchor4 = None
            closest_pair_to_ninety_anchor4 = None
            closest_distance_anchor4 = None
            ########################################################

            # หาค่าที่ใกล้เคียง 90° มากที่สุดใน Anchor1 แล้วเก็บค่าตัวแปรที่สร้างไว้
            for theta_values, pairs in zip(result_theta_alpha_beta, result_pair_alpha_beta):
                closest_value, closest_pair, row_index, distance = find_closest_to_ninety_anchor1(result_theta_alpha_beta, result_pair_alpha_beta, range(len(result_theta_alpha_beta)), rows_from_QLH_onward)
                if closest_value is not None:
                    if closest_to_ninety_anchor1 is None or abs(90 - closest_value) < abs(90 - closest_to_ninety_anchor1):
                        closest_to_ninety_anchor1 = closest_value
                        closest_pair_to_ninety_anchor1 = closest_pair
                        closest_distance_anchor1 = distance
                
            # หาค่าที่ใกล้เคียง 90° มากที่สุดใน Anchor2 แล้วเก็บค่าตัวแปรที่สร้างไว้      
            for theta_values, pairs in zip(result_theta_phi_delta, result_pair_phi_delta):
                closest_value, closest_pair, row_index, distance = find_closest_to_ninety_anchor2(result_theta_phi_delta, result_pair_phi_delta, range(len(result_theta_phi_delta)), rows_from_QRH_onward)
                if closest_value is not None:
                    if closest_to_ninety_anchor2 is None or abs(90 - closest_value) < abs(90 - closest_to_ninety_anchor2):
                        closest_to_ninety_anchor2 = closest_value
                        closest_pair_to_ninety_anchor2 = closest_pair
                        closest_distance_anchor2 = distance


        #################################เพิ่มเพิ่มเติมเพื่อหาค่าที่ใกล้เคียง 90° มากที่สุดใน Anchor3 แล้วเก็บค่าตัวแปรที่สร้างไว้####################################
            # หาค่าที่ใกล้เคียง 90° มากที่สุดใน Anchor3 แล้วเก็บค่าตัวแปรที่สร้างไว้      
            for theta_values, pairs in zip(result_theta_phi_delta, result_pair_phi_delta):
                closest_value, closest_pair, row_index, distance = find_closest_to_ninety_anchor3(result_theta_phi_delta, result_pair_phi_delta, range(len(result_theta_phi_delta)), rows_from_QRH_onward)
                if closest_value is not None:
                    if closest_to_ninety_anchor2 is None or abs(90 - closest_value) < abs(90 - closest_to_ninety_anchor2):
                        closest_to_ninety_anchor2 = closest_value
                        closest_pair_to_ninety_anchor2 = closest_pair
                        closest_distance_anchor2 = distance

                # หาค่าที่ใกล้เคียง 90° มากที่สุดใน Anchor4 แล้วเก็บค่าตัวแปรที่สร้างไว้      
            for theta_values, pairs in zip(result_theta_phi_delta, result_pair_phi_delta):
                closest_value, closest_pair, row_index, distance = find_closest_to_ninety_anchor4(result_theta_phi_delta, result_pair_phi_delta, range(len(result_theta_phi_delta)), rows_from_QRH_onward)
                if closest_value is not None:
                    if closest_to_ninety_anchor2 is None or abs(90 - closest_value) < abs(90 - closest_to_ninety_anchor2):
                        closest_to_ninety_anchor2 = closest_value
                        closest_pair_to_ninety_anchor2 = closest_pair
                        closest_distance_anchor2 = distance
        ###############################################################################################################################
                        
            # แสดงผลลัพธ์ของค่า theta ที่ใกล้ 90 ที่สุด
            # Anchor1
            if closest_to_ninety_anchor1 is not None:
                print(f"The value closest to 90 is (Anchor1): {closest_to_ninety_anchor1:.5f}")
                print(f"Corresponding pair (alpha, beta): [{closest_pair_to_ninety_anchor1[0]:.5f}, {closest_pair_to_ninety_anchor1[1]:.5f}]")
                print(f"Distance (meter): {closest_distance_anchor1}\n")
            else:
                print("No valid theta values found.\n")

            # Anchor2
            if closest_to_ninety_anchor2 is not None:
                print(f"The value closest to 90 is (Anchor2): {closest_to_ninety_anchor2:.5f}")
                print(f"Corresponding pair (phi, delta): [{closest_pair_to_ninety_anchor2[0]:.5f}, {closest_pair_to_ninety_anchor2[1]:.5f}]")
                print(f"Distance (meter): {closest_distance_anchor2}\n")
            else:
                print("No valid theta values found.\n")

#############################เพิ่ม Anchor3 และ Anchor4 ที่สร้างไว้ในการคำนวณหาค่า theta ที่ใกล้ 90 ที่สุด
            # Anchor3
            if closest_to_ninety_anchor3 is not None:
                print(f"The value closest to 90 is (Anchor3): {closest_to_ninety_anchor3:.5f}")
                print(f"Corresponding pair (alpha, beta): [{closest_pair_to_ninety_anchor3[0]:.5f}, {closest_pair_to_ninety_anchor3[1]:.5f}]")
                print(f"Distance (meter): {closest_distance_anchor3}\n")
            else:
                print("No valid theta values found.\n")
            
            # Anchor4
            if closest_to_ninety_anchor4 is not None:
                print(f"The value closest to 90 is (Anchor4): {closest_to_ninety_anchor4:.5f}")
                print(f"Corresponding pair (alpha, beta): [{closest_pair_to_ninety_anchor4[0]:.5f}, {closest_pair_to_ninety_anchor4[1]:.5f}]")
                print(f"Distance (meter): {closest_distance_anchor4}\n")
            else:
                print("No valid theta values found.\n")
#########################################################################################

            # คำนวณ result_alpha_lin สำหรับค่า alpha ที่มี distance เดียวกับ closest_distance_anchor1
            result_alpha_lin = []
            for _, row in rows_from_LL_onward.iterrows():
                if row['distance'] == closest_distance_anchor1:
                    a = row['a']
                    b = row['b']
                    alpha = ((rssi_hor_1 - rssi_ver_1) - b) / a
                    # if alpha > 90:
                    #     alpha = alpha % 90
                    result_alpha_lin.append(alpha)


            # คำนวณ result_phi_lin สำหรับค่า phi ที่มี distance เดียวกับ closest_distance_anchor2
            result_phi_lin = []
            for _, row in rows_from_LR_onward.iterrows():
                if row['distance'] == closest_distance_anchor2:
                    a = row['a']
                    b = row['b']
                    phi = ((rssi_hor_2 - rssi_ver_2) - b) / a
                    # if phi > 90:
                    #     phi = phi % 90
                    result_phi_lin.append(phi)   
            print(f"alpha_linear: {result_alpha_lin}")
            print(f"phi_linear: {result_phi_lin}")
            
            ##################เพิ่ม  Anchor3 และ Anchor4 ที่สร้างไว้ในการคำนวณหาค่า theta ที่ใกล้ 90 ที่สุด##################
                # คำนวณ result_alpha_lin สำหรับค่า alpha ที่มี distance เดียวกับ closest_distance_anchor3
            result_alpha_lin = []
            for _, row in rows_from_LL_onward.iterrows():
                if row['distance'] == closest_distance_anchor3:
                    a = row['a']
                    b = row['b']
                    alpha = ((rssi_hor_3 - rssi_ver_3) - b) / a
                    # if alpha > 90:
                    #     alpha = alpha % 90
                    result_alpha_lin.append(alpha)

                # คำนวณ result_alpha_lin สำหรับค่า alpha ที่มี distance เดียวกับ closest_distance_anchor1
            result_alpha_lin = []
            for _, row in rows_from_LL_onward.iterrows():
                if row['distance'] == closest_distance_anchor4:
                    a = row['a']
                    b = row['b']
                    alpha = ((rssi_hor_4 - rssi_ver_4) - b) / a
                    # if alpha > 90:
                    #     alpha = alpha % 90
                    result_alpha_lin.append(alpha)
            ######################################################################


            # จับคู่ alpha และ phi ที่คำนวณได้จาก result_alpha_lin และ result_phi_lin
            result_pair_alpha_phi = []
            alpha11 = None
            phi11 = None
            for i, (alpha, phi) in enumerate(zip(result_alpha_lin, result_phi_lin)):
                result_pair_alpha_phi.append((alpha, phi))
                alpha11 = alpha
                phi11 = phi


            # คำนวณหา x, y จาก alpha และ phi แล้ว return x, y กลับมา
            def estimate_position(D, alpha, phi):
                epsilon = 1e-6  # ค่ามุมเล็ก ๆ
                if alpha == 0:
                    alpha += epsilon
                if phi == 0:
                    phi += epsilon
                x = (D * math.tan(math.radians(phi))) / (math.tan(math.radians(alpha)) + math.tan(math.radians(phi)))
                y = (D * math.tan(math.radians(alpha)) * math.tan(math.radians(phi))) / (math.tan(math.radians(alpha)) + math.tan(math.radians(phi)))
                return x, y

            D = 15.00
            if alpha11 is not None and phi11 is not None:
                x1, y1 = estimate_position(D, alpha11, phi11)
                # print(f"Estimate Position: {x1:.2f}, {abs(y1):.2f}")
                print(f"Estimate Position: {x1:.2f}, {y1:.2f}")
                
            return x1,y1
        
        
        #--------------------------------------------------------------------------
        #RSSI calculation algorithm
        
        def process_rssi(self, A1_V, A1_H, A2_V, A2_H, A3_V, A3_H, A4_V, A4_H):
            def calculation_distance(rssi, A, n):
                distance = 10 ** ((A - rssi) / (10 * n))
                return distance

        #ค่าเหล่านี้ได้มาจาก:
        # วางอุปกรณ์ห่างกัน 1 เมตรพอดี
        # วัดค่า RSSI หลายครั้ง
        # หาค่าเฉลี่ย
        # ใช้เป็นค่าอ้างอิง (Reference) สำหรับคำนวณระยะทาง 
                
            # RSSI 1 m. at Anchor 1
            A_hor_1 = -48  # สัญญาณแรงกว่า (ใกล้ 0 = แรงกว่า)
            A_ver_1 = -47  # สัญญาณอ่อนกว่า (ไกล 0 = อ่อนกว่า)

            # RSSI 1 m. at Anchor 2
            A_hor_2 = -59
            A_ver_2 = -54
                                
            # RSSI 1 m. at Anchor 3                  
            A_hor_3 = -52  # ค่าที่ต้อง calibrate จริง
            A_ver_3 = -50  # ค่าที่ต้อง calibrate จริง

            # RSSI 1 m. at Anchor 4 
            A_hor_4 = -55  # ค่าที่ต้อง calibrate จริง
            A_ver_4 = -53  # ค่าที่ต้อง calibrate จริง


            # RSSI 1 m. combined
            A_all_1 = round((A_hor_1 + A_ver_1) / 2)
            A_all_2 = round((A_hor_2 + A_ver_2) / 2)
            A_all_3 = round((A_hor_3 + A_ver_3) / 2)
            A_all_4 = round((A_hor_4 + A_ver_4) / 2)

            n_1 = 1.5
            n_2 = 1.5
            n_3 = 1.5
            n_4 = 1.5
            
            rssi_ver_1 = A1_V
            rssi_ver_2 = A2_V
            rssi_hor_1 = A1_H
            rssi_hor_2 = A2_H

            #######เพิ่ม Anchor3 และ Anchor4 ที่สร้างไว้ในการคำนวณหาค่า theta ที่ใกล้ 90 ที่สุด##################
            rssi_ver_3 = A3_V
            rssi_ver_4 = A4_V
            rssi_hor_3 = A3_H
            rssi_hor_4 = A4_H
            ############################################################

            average_1 = round((rssi_hor_1 + rssi_ver_1) / 2)
            average_2 = round((rssi_hor_2 + rssi_ver_2) / 2)

            #เพิ่ม Anchor3 และ Anchor4 ที่สร้างไว้ในการคำนวณหาค่า theta ที่ใกล้ 90 ที่สุด##################
            average_3 = round((rssi_hor_3 + rssi_ver_3) / 2)
            average_4 = round((rssi_hor_4 + rssi_ver_4) / 2)
            ############################################################

            # distance Anchor 1
            distance_avg_1 = calculation_distance(average_1, A_all_1, n_1)
            distance_hor_1 = calculation_distance(rssi_hor_1, A_hor_1, n_1)
            distance_ver_1 = calculation_distance(rssi_ver_1, A_ver_1, n_1)

            # distance Anchor 2
            distance_avg_2 = calculation_distance(average_2, A_all_2, n_2)
            distance_hor_2 = calculation_distance(rssi_hor_2, A_hor_2, n_2)
            distance_ver_2 = calculation_distance(rssi_ver_2, A_ver_2, n_2)
            
            # distance Anchor 3
            distance_avg_3 = calculation_distance(average_3, A_all_3, n_3)
            distance_hor_3 = calculation_distance(rssi_hor_3, A_hor_3, n_3)
            distance_ver_3 = calculation_distance(rssi_ver_3, A_ver_3, n_3)

            # distance Anchor 4
            distance_avg_4 = calculation_distance(average_3, A_all_4, n_4)
            distance_hor_4 = calculation_distance(rssi_hor_3, A_hor_4, n_4)
            distance_ver_4 = calculation_distance(rssi_ver_3, A_ver_4, n_4)
            
            


            print(f"average (1): {distance_avg_1:.3f}")
            print(f"average (2): {distance_avg_2:.3f}\n")

            print(f"hor (1): {distance_hor_1:.3f}")
            print(f"hor (2): {distance_hor_2:.3f}\n")

            print(f"ver (1): {distance_ver_1:.3f}")
            print(f"ver (2): {distance_ver_2:.3f}\n")

            print(f"average (3): {distance_avg_3:.3f}")
            print(f"average (4): {distance_avg_4:.3f}\n")

            print(f"hor (3): {distance_hor_3:.3f}")
            print(f"hor (4): {distance_hor_4:.3f}\n")

            print(f"ver (3): {distance_ver_3:.3f}")
            print(f"ver (4): {distance_ver_4:.3f}\n")


            def find_coordinates(x1, y1, distance1, x2, y2, distance2):
                if y1 == y2:
                    #Use distance and circle equation to calculate y values
                    A = 2 * (x2 - x1)
                    B = 2 * (y2 - y1)
                    C = distance1**2 - distance2**2 - x1**2 + x2**2 - y1**2 + y2**2

                    if A != 0:  #Calculate the x value first.
                        x = C / A

                        #Substitute the x value back into the circle equation to find the y value
                        term1 = distance1**2 - (x - x1)**2
                
                        if term1 >= 0:  #Check term1 is not negative (to avoid sqrt of negative values)
                            y = y1 + (term1**0.5)  #calculate y
                            return x, y
                        else:
                            # raise ValueError("The distance is unreasonable, causing the result to be incomputable.")
                            #Can't calculate But there is a value displayed on the screen
                            print("The distance is unreasonable, causing the result to be incomputable.")
                            x = -1
                            y = -1
                            return x, y
                    else:
                        raise ValueError("A has a value of zero, so x cannot be calculated.")

            x1, y1 = 0, 0  #Anchor 1
            x2, y2 = 15.00, 0  #Anchor 2

            try:
                x_ver, y_ver = find_coordinates(x1, y1, distance_ver_1, x2, y2, distance_ver_2)
                # print(f"Coordinates (ver): ({x_ver:.2f}, {y_ver:.2f})")
            except ValueError as e:
                print(e)
                
            return x_ver,y_ver
if __name__ == "__main__":
    MyApp().run()