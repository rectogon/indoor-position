from pyobjus import autoclass, objc_str
from pyobjus.dylib_manager import load_framework, INCLUDE


from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock, mainthread

load_framework(INCLUDE.Foundation)

BluetoothBridge = autoclass('BluetoothBridge')
NSDictionary = autoclass('NSDictionary')

class BluetoothScanApp(App):

    def build(self):
        self.label = Label(text="Initializing Bluetooth...")
        self.bridge = BluetoothBridge.alloc().init()
        self.bridge.startBluetoothScan()

        Clock.schedule_interval(self.check_discovered_device, 1.0)
        return self.label

    @mainthread
    def check_discovered_device(self, dt):
        device = self.bridge.getLastDiscoveredDevice()
        if device:
            name = device.objectForKey_(objc_str("name")).UTF8String()
            uuid = device.objectForKey_(objc_str("uuid")).UTF8String()
            rssi = device.objectForKey_(objc_str("rssi")).intValue()
            major = device.objectForKey_(objc_str("major")).intValue()
            minor = device.objectForKey_(objc_str("minor")).intValue()

            display_text = f"Device: {name}\nUUID: {uuid}\nRSSI: {rssi}\nMajor: {major} Minor: {minor}"
            print(display_text)
            self.label.text = display_text

    def on_stop(self):
        self.bridge.stopBluetoothScan()

if __name__ == '__main__':
    BluetoothScanApp().run()
