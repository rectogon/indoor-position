import Foundation
import CoreBluetooth

@objc protocol BluetoothScanDelegate {
    func didDiscoverDevice(name: String?, uuid: String, rssi: Int, major: Int, minor: Int)
}

@objcMembers
class BluetoothManager: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate {
    var centralManager: CBCentralManager?
    
    weak var delegate: BluetoothScanDelegate?
    var discoveredPeripherals: [UUID: CBPeripheral] = [:]
    var disconnectedPeripherals: [UUID: CBPeripheral] = [:] // เก็บ peripheral ที่ disconnect แล้ว
    private var _autoReconnect: Bool = false // เปลี่ยนเป็น private
    var maxReconnectAttempts1: Int = 3
    var reconnectAttempts: [UUID: Int] = [:]
    
    // เพิ่มตัวแปรสำหรับเก็บข้อมูล UI รวมทั้ง RSSI
    private var _uuid: String = ""
    private var _major: Int = 0
    private var _minor: Int = 0
    private var _rssi: Int = 0  // เพิ่ม RSSI
    private var _name: String = ""  // เพิ่ม name

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }

    // อัพเดท updateUI method ให้รวม RSSI
    @objc(updateUIWithName:rssi:)
    func updateUI(name: String, rssi: Int) {
        // อัพเดท RSSI ปัจจุบัน
        _rssi = rssi
        _name = name
        
        let scannedInfo = "\(name), RSSI: \(rssi) dBm\nUUID: \(_uuid)\nMajor: \(_major), Minor: \(_minor)"
        
        print("Swift updateUI called with:")
        print("Name: \(name)")
        print("RSSI: \(rssi)")
        print("UUID: \(_uuid)")
        print("Major: \(_major), Minor: \(_minor)")
        print("Scanned Info: \(scannedInfo)")
        
        // ส่งข้อมูลกลับไปยัง delegate หรือ callback
        // สามารถเพิ่ม delegate method สำหรับ UI update ได้
    }
    
    // อัพเดท setDeviceInfo method ให้รวม RSSI
    @objc(setDeviceInfoWithUUID:major:minor:rssi:name:)
    func setDeviceInfo(uuid: String, major: Int, minor: Int, rssi: Int, name: String) {
        _uuid = uuid
        _major = major
        _minor = minor
        _rssi = rssi
        _name = name
        print("Device info updated - UUID: \(uuid), Major: \(major), Minor: \(minor), RSSI: \(rssi), Name: \(name)")
    }
    
    // เพิ่ม method สำหรับ set แค่ RSSI
    @objc(updateRSSI:)
    func updateRSSI(_ rssi: Int) {
        _rssi = rssi
        print("RSSI updated to: \(rssi)")
        
        // อัพเดท UI ด้วย RSSI ใหม่
        if !_name.isEmpty {
            updateUI(name: _name, rssi: rssi)
        }
    }
    
    // เพิ่ม getter methods
    @objc var currentRSSI: Int {
        return _rssi
    }
    
    @objc var currentDeviceName: String {
        return _name
    }
    
    @objc var currentUUID: String {
        return _uuid
    }
    
    @objc var currentMajor: Int {
        return _major
    }
    
    @objc var currentMinor: Int {
        return _minor
    }

    // เพิ่ม method สำหรับดึงข้อมูลทั้งหมด
    @objc func getCurrentDeviceInfo() -> NSDictionary {
        return [
            "name": _name,
            "uuid": _uuid,
            "rssi": _rssi,
            "major": _major,
            "minor": _minor,
            "timestamp": Date().timeIntervalSince1970
        ]
    }

    func startScan() {
        guard let manager = centralManager else { return }
        if manager.state == .poweredOn {
            manager.scanForPeripherals(withServices: nil, options: nil)
            print("Swift: Scanning started")
        }
    }

    func stopScan() {
        centralManager?.stopScan()
        print("Swift: Scanning stopped")
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral,
                        advertisementData: [String : Any], rssi RSSI: NSNumber) {
        let uuid = peripheral.identifier.uuidString
        let name = peripheral.name ?? "Unknown"
        discoveredPeripherals[peripheral.identifier] = peripheral

        var major = 0
        var minor = 0

        if let manufacturerData = advertisementData[CBAdvertisementDataManufacturerDataKey] as? Data {
            if manufacturerData.count >= 25 {
                major = Int(manufacturerData[20]) << 8 | Int(manufacturerData[21])
                minor = Int(manufacturerData[22]) << 8 | Int(manufacturerData[23])
            }
        }

        // อัพเดทข้อมูล device ปัจจุบัน รวมทั้ง RSSI
        setDeviceInfo(uuid: uuid, major: major, minor: minor, rssi: RSSI.intValue, name: name)
        
        // เรียก updateUI
        updateUI(name: name, rssi: RSSI.intValue)

        delegate?.didDiscoverDevice(name: name, uuid: uuid, rssi: RSSI.intValue, major: major, minor: minor)
    }

    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        print("Bluetooth state changed: \(central.state.rawValue)")
    }
    @objc(connectToPeripheralWith:)
    func connectToPeripheral(uuidString: String) {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            print("Peripheral with UUID \(uuidString) not found")
            return
        }

        centralManager?.connect(peripheral, options: nil)
    }
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("✅ Connected to peripheral: \(peripheral.name ?? "Unknown")")
        //////////////////
        
        // รีเซ็ต reconnect attempts เมื่อเชื่อมต่อสำเร็จ
        reconnectAttempts[peripheral.identifier] = 0
        
        // ย้ายจาก disconnected กลับไป discovered
        if disconnectedPeripherals[peripheral.identifier] != nil {
            disconnectedPeripherals.removeValue(forKey: peripheral.identifier)
            discoveredPeripherals[peripheral.identifier] = peripheral
        }
        
        ///////////////////
        peripheral.delegate = self
        peripheral.discoverServices(nil)////////////////////
    
    }///////////////////////
//////////////////////////////////////
    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        print("❌ Disconnected from peripheral: \(peripheral.name ?? "Unknown")")
        
        // เก็บ peripheral ที่ disconnect ไว้สำหรับ reconnect
        disconnectedPeripherals[peripheral.identifier] = peripheral
        
        // ลบ threading logic ออก - ให้ bridge จัดการ
        // Auto reconnect ถ้าเปิดใช้งาน
        if _autoReconnect {
            // แค่เรียก reconnect ตรงๆ หรือให้ bridge จัดการ timing
            let peripheralUUID = peripheral.identifier.uuidString
            // อาจจะเรียกผ่าน delegate callback แทน
            print("Auto reconnect requested for: \(peripheralUUID)")
        }
    }

    func centralManager(_ central: CBCentralManager, didFailToConnect peripheral: CBPeripheral, error: Error?) {
        print("❌ Failed to connect to peripheral: \(peripheral.name ?? "Unknown"), error: \(error?.localizedDescription ?? "Unknown")")
        
        // ลบ threading logic ออก
        if _autoReconnect {
            let peripheralUUID = peripheral.identifier.uuidString
            let currentAttempts = reconnectAttempts[peripheral.identifier] ?? 0
            if currentAttempts < maxReconnectAttempts1 {
                print("Auto reconnect requested for: \(peripheralUUID)")
                // ให้ bridge หรือ Python layer จัดการ timing
            }
        }
    }

    @objc(reconnectToPeripheralWith:)
    func reconnectToPeripheral(uuidString: String) {
        print("Device: \(uuidString) try to reconnect ...")
        
        guard let uuid = UUID(uuidString: uuidString) else {
            print("Invalid UUID string: \(uuidString)")
            return
        }
        
        // หา peripheral จาก discovered หรือ disconnected
        var peripheral: CBPeripheral?
        
        if let discoveredPeripheral = discoveredPeripherals[uuid] {
            peripheral = discoveredPeripheral
        } else if let disconnectedPeripheral = disconnectedPeripherals[uuid] {
            peripheral = disconnectedPeripheral
        }
        
        guard let targetPeripheral = peripheral else {
            print("Peripheral with UUID \(uuidString) not found for reconnection")
            return
        }
        
        // เช็ค reconnect attempts
        let currentAttempts = reconnectAttempts[uuid] ?? 0
        if currentAttempts >= maxReconnectAttempts1 {
            print("Max reconnect attempts reached for device: \(uuidString)")
            return
        }
        
        // เพิ่ม attempt count
        reconnectAttempts[uuid] = currentAttempts + 1
        
        // ทำการ reconnect
        centralManager?.connect(targetPeripheral, options: nil)
        print("Reconnection attempt \(currentAttempts + 1)/\(maxReconnectAttempts1) for device: \(targetPeripheral.name ?? "Unknown")")
    }

    @objc(disconnectPeripheralWith:)
    func disconnectPeripheral(uuidString: String) {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            print("Peripheral with UUID \(uuidString) not found for disconnection")
            return
        }
        
        centralManager?.cancelPeripheralConnection(peripheral)
        print("Disconnecting from peripheral: \(peripheral.name ?? "Unknown")")
    }

    @objc(enableAutoReconnect:)
    func enableAutoReconnect(_ enabled: Bool) {
        _autoReconnect = enabled
        print("Auto reconnect set to: \(enabled)")
    }

    @objc(configureMaxReconnectAttempts:)
    func configureMaxReconnectAttempts(_ attempts: Int) {
        maxReconnectAttempts1 = attempts
        print("Max reconnect attempts set to: \(attempts)")
    }

    @objc var isAutoReconnectEnabled: Bool {
        return _autoReconnect
    }

    @objc func getConnectedPeripheralsCount() -> Int {
        let connectedPeripherals = centralManager?.retrieveConnectedPeripherals(withServices: []) ?? []
        return connectedPeripherals.count
    }

    // เพิ่มใน BluetoothManager class
    @objc(setAutoReconnect:)
    func setAutoReconnect(_ enabled: Bool) {
        _autoReconnect = enabled
        print("setAutoReconnect called with: \(enabled)")
    }

    @objc(setMaxReconnectAttempts:)
    func setMaxReconnectAttempts(_ attempts: Int) {
        maxReconnectAttempts1 = attempts
        print("setMaxReconnectAttempts called with: \(attempts)")
    }

    // เพิ่ม method สำหรับ auto reconnect handler
    typealias ReconnectHandler = (String) -> Void
    var autoReconnectHandler1: ReconnectHandler?

    @objc func setAutoReconnectHandler(_ handler: @escaping ReconnectHandler) {
        autoReconnectHandler1 = handler
    }

    // เพิ่ม method ที่หายไป
    @objc(startRSSIUpdatesForPeripheral:)
    func startRSSIUpdates(uuidString: String) {
        print("startRSSIUpdatesForPeripheral called with: \(uuidString)")
        
        guard let uuid = UUID(uuidString: uuidString) else {
            print("❌ Invalid UUID string: \(uuidString)")
            return
        }
        
        // หา peripheral จาก discovered หรือ connected
        var peripheral: CBPeripheral?
        
        if let discoveredPeripheral = discoveredPeripherals[uuid] {
            peripheral = discoveredPeripheral
        } else if let disconnectedPeripheral = disconnectedPeripherals[uuid] {
            peripheral = disconnectedPeripheral
        }
        
        guard let targetPeripheral = peripheral else {
            print("❌ Peripheral with UUID \(uuidString) not found for RSSI updates")
            return
        }
        
        // ตั้ง delegate และเริ่ม read RSSI
        targetPeripheral.delegate = self
        targetPeripheral.readRSSI()
        
        print("✅ Started RSSI updates for: \(targetPeripheral.name ?? "Unknown")")
    }
    
    // เพิ่ม method สำหรับ stop RSSI updates
    @objc(stopRSSIUpdatesForPeripheral:)
    func stopRSSIUpdates(uuidString: String) {
        print("stopRSSIUpdatesForPeripheral called with: \(uuidString)")
        // Implementation สำหรับหยุด RSSI updates ถ้าจำเป็น
    }
    
    // เพิ่ม method สำหรับ get current RSSI
    @objc(getCurrentRSSIForPeripheral:)
    func getCurrentRSSI(uuidString: String) -> Int {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            print("❌ Peripheral not found for RSSI check")
            return -999 // Error value
        }
        
        // Return cached RSSI หรือ trigger new read
        peripheral.readRSSI()
        return _rssi // Return current cached value
    }
}

@objc protocol BluetoothBridgeDelegate {
    @objc optional func didConnectToDevice(uuid: String)
    @objc optional func didDisconnectFromDevice(uuid: String, error: Error?)
    @objc optional func didFailToConnectToDevice(uuid: String, error: Error?)
}
/////////////////////////
