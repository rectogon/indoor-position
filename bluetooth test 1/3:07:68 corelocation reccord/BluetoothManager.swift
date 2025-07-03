import Foundation
import CoreBluetooth
import UIKit
import CoreLocation


@objc protocol BluetoothScanDelegate {
    func didDiscoverDevice(name: String?, uuid: String, rssi: Int, major: Int, minor: Int)
}

@objcMembers
class BluetoothManager: NSObject, CBCentralManagerDelegate, CBPeripheralDelegate,CLLocationManagerDelegate {
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
    private var _discoveredDevices: [[String: Any]] = []

/////////***เพิ่มตัวแปรเก็บข้อมูลแบตเตอรี่***////////////
    private var batteryInfo: [String: Any] = [:]
    private var lastCharacteristicData: [String: Any] = [:]
/////////////////////////////////////////
 
    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
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

    @objc(didDiscoverDeviceWithName:uuid:rssi:major:minor:)
    func didDiscoverDevice(name: String?, uuid: String, rssi: Int, major: Int, minor: Int) {
        
        NSLog("BluetoothBridge: Device discovered - Name: %@, UUID: %@, RSSI: %ld, Major: %ld, Minor: %ld",
            name ?? "Unknown", uuid, rssi, major, minor)
        
        let deviceInfo: [String: Any] = [
            "name": name ?? "Unknown",
            "uuid": uuid,
            "rssi": rssi,
            "major": major,
            "minor": minor,
            "timestamp": Date().timeIntervalSince1970
        ]
        
        self.lastDevice = deviceInfo
        
        // Check if device already exists in discovered devices
        var deviceExists = false
        for (index, existingDevice) in _discoveredDevices.enumerated() {
            if let existingUUID = existingDevice["uuid"] as? String, existingUUID == uuid {
                // Update existing device info
                _discoveredDevices[index] = deviceInfo
                deviceExists = true
                break
            }
        }
        
        if !deviceExists {
            _discoveredDevices.append(deviceInfo)
        }
        
        NSLog("BluetoothBridge: Total discovered devices: %lu", _discoveredDevices.count)
    }

    

    @objc var discoveredDevices: [[String: Any]] {
        return _discoveredDevices
    }

    @objc func getDiscoveredDevicesCount() -> Int {
    return _discoveredDevices.count
    }

    @objc func clearDiscoveredDevices() {
    _discoveredDevices.removeAll()
    NSLog("BluetoothBridge: Cleared all discovered devices")
    }

    @objc(getDiscoveredDeviceByUUID:)
    func getDiscoveredDevice(uuid: String) -> [String: Any]? {
        return _discoveredDevices.first { device in
            if let deviceUUID = device["uuid"] as? String {
                return deviceUUID == uuid
            }
            return false
        }
    }

    private var _lastDevice: [String: Any]?
    @objc var lastDevice: [String: Any]? {
        get { return _lastDevice }
        set { _lastDevice = newValue }
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
              let peripheral = discoveredPeripherals[uuid],
              peripheral.state == .connected else {
            print("❌ Peripheral not found or not connected for RSSI check")
            return -999
        }
        
        // ✅ Force อ่าน RSSI ใหม่ทุกครั้ง
        peripheral.delegate = self
        peripheral.readRSSI()
        
        print("🔄 Requested fresh RSSI read for: \(peripheral.name ?? "Unknown")")
        
        // Return ค่าปัจจุบัน (จะได้ค่าใหม่ใน delegate)
        return _rssi
    }

    @objc func stopScan() {
    print("🚨 Swift stopScan CALLED")
    
    guard let manager = centralManager else {
        print("❌ centralManager is nil")
        return
    }
    
    if manager.isScanning {
        manager.stopScan()
        print("🛑 Swift: Stopped scanning for peripherals.")
    } else {
        print("⚠️ Swift: Already not scanning")
    }
}






    ///***Gatt initiation***
    var connectedServices: [UUID: [CBService]] = [:]
    var availableCharacteristics: [UUID: [CBCharacteristic]] = [:]

    // เพิ่ม CBPeripheralDelegate methods ที่ขาดหายไป

    //////////////////////** การค้นหา services **//////////////////////////////////

    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard error == nil else {
            print("❌ Error discovering services: \(error!.localizedDescription)")
            return
        }
        
        print("✅ Services discovered for \(peripheral.name ?? "Unknown")")
        
        if let services = peripheral.services {
            connectedServices[peripheral.identifier] = services
            
            for service in services {
                print("📋 Service found: \(service.uuid)")  
                // Discover characteristics for each service
                peripheral.discoverCharacteristics(nil, for: service)
            }
        }
    }
    /////////////////////////////////////////////////////////////////////////////////


      /////////**การค้นหา Characteristics**////////////////////////////////////
    

//     //Properties: CBCharacteristicProperties(rawValue: 2)   // Read only
// Properties: CBCharacteristicProperties(rawValue: 18)  // Read + Notify  
// Properties: CBCharacteristicProperties(rawValue: 152) // Write + Notify + 
//WriteWithoutResponse

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard error == nil else {
            print("❌ Error discovering characteristics: \(error!.localizedDescription)")
            return
        }
        
        print("✅ Characteristics discovered for service: \(service.uuid)") 
        
        if let characteristics = service.characteristics {
            // เก็บ characteristics
            if availableCharacteristics[peripheral.identifier] == nil {
                availableCharacteristics[peripheral.identifier] = []
            }
            availableCharacteristics[peripheral.identifier]?.append(contentsOf: characteristics)
            
            for characteristic in characteristics {
                print("📝 Characteristic: \(characteristic.uuid)")
                print("   Properties: \(characteristic.properties)")
                
                // Subscribe to notifications if available
                if characteristic.properties.contains(.notify) {
                    peripheral.setNotifyValue(true, for: characteristic)
                    print("🔔 Subscribed to notifications for: \(characteristic.uuid)")
                }
                
                // Read value if readable
                if characteristic.properties.contains(.read) {
                    peripheral.readValue(for: characteristic)
                    print("📖 Reading value for: \(characteristic.uuid)")
                }
            }
        }
 ///////////////////////////////////////////////////////////////////////////



    }
    // เพิ่ม methods สำหรับ read/write data
    @objc(readCharacteristicForDevice:serviceUUID:characteristicUUID:)
    func readCharacteristic(deviceUUID: String, serviceUUID: String, characteristicUUID: String) {
        guard let uuid = UUID(uuidString: deviceUUID),
              let peripheral = discoveredPeripherals[uuid],
              peripheral.state == .connected else {
            print("❌ Device not connected for reading")
            return
        }
        
        let serviceUUIDObj = CBUUID(string: serviceUUID)
        let charUUIDObj = CBUUID(string: characteristicUUID)
        
        if let service = peripheral.services?.first(where: { $0.uuid == serviceUUIDObj }),
           let characteristic = service.characteristics?.first(where: { $0.uuid == charUUIDObj }) {
            peripheral.readValue(for: characteristic)
            print("📖 Reading characteristic: \(characteristicUUID)")
        } else {
            print("❌ Characteristic not found")
        }
    }

    @objc(writeData:toDevice:serviceUUID:characteristicUUID:)
    func writeData(data: Data, deviceUUID: String, serviceUUID: String, characteristicUUID: String) {
        guard let uuid = UUID(uuidString: deviceUUID),
              let peripheral = discoveredPeripherals[uuid],
              peripheral.state == .connected else {
            print("❌ Device not connected for writing")
            return
        }
        
        let serviceUUIDObj = CBUUID(string: serviceUUID)
        let charUUIDObj = CBUUID(string: characteristicUUID)
        
        if let service = peripheral.services?.first(where: { $0.uuid == serviceUUIDObj }),
           let characteristic = service.characteristics?.first(where: { $0.uuid == charUUIDObj }) {
            
            let writeType: CBCharacteristicWriteType = characteristic.properties.contains(.writeWithoutResponse) ? .withoutResponse : .withResponse
            peripheral.writeValue(data, for: characteristic, type: writeType)
            print("✍️ Writing data to characteristic: \(characteristicUUID)")
        } else {
            print("❌ Characteristic not found for writing")
        }
    }


    /////////**Data Reception (การรับข้อมูล)+methodจัดการแบตเตอรี่**////////////////////////////////////

    // Handle read/write responses
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let data = characteristic.value else { return }
        let charName = getCharacteristicName(for: characteristic.uuid)
        print("📨 Data received from \(charName): \(data.count) bytes")
        
        // ✅ จัดการข้อมูลแบตเตอรี่เป็นพิเศษ
        if characteristic.uuid.uuidString == "2A19" {  // Battery Level UUID
            if data.count >= 1 {
                let batteryLevel = data[0]
                print("🔋 Battery Level: \(batteryLevel)%")
                
                // อัพเดทข้อมูลแบตเตอรี่
                updateBatteryInfo(level: Int(batteryLevel), deviceUUID: peripheral.identifier.uuidString, deviceName: peripheral.name ?? "Unknown")
            }
        }
        
        // แปลงเป็น string
        if let stringValue = String(data: data, encoding: .utf8) {
            print("📨 Data as string: \(stringValue)")
            
            // ถ้าเป็น Model Number String ให้แปลงเป็นชื่อจริง
            if characteristic.uuid.uuidString == "2A24" {
                let actualModel = getDeviceModel(identifier: stringValue)
                print("📱 Actual Device Model: \(actualModel)")
            }
        }
        
        // แปลงเป็น hex
        let hexString = data.map { String(format: "%02x", $0) }.joined()
        print("📨 Data as hex: \(hexString)")
        
        // สร้าง dictionary พร้อมข้อมูลที่แปลงแล้ว
        var characteristicData: [String: Any] = [
            "deviceUUID": peripheral.identifier.uuidString,
            "deviceName": peripheral.name ?? "Unknown",
            "characteristicUUID": characteristic.uuid.uuidString,
            "data": data.base64EncodedString(),
            "timestamp": Date().timeIntervalSince1970
        ]
        
        // เพิ่มข้อมูลที่แปลงแล้วถ้าเป็น Model Number
        if characteristic.uuid.uuidString == "2A24",
           let modelIdentifier = String(data: data, encoding: .utf8) {
            characteristicData["modelIdentifier"] = modelIdentifier
            characteristicData["actualModel"] = getDeviceModel(identifier: modelIdentifier)
        }
        
        // ✅ เพิ่มข้อมูลแบตเตอรี่ถ้าเป็น Battery Level
        if characteristic.uuid.uuidString == "2A19", data.count >= 1 {
            let batteryLevel = Int(data[0])
            characteristicData["batteryLevel"] = batteryLevel
            characteristicData["batteryStatus"] = getBatteryStatus(level: batteryLevel)
        }
        
        print("📊 Updated characteristic data: \(characteristicData)")
        lastCharacteristicData = characteristicData
    }
    ///////////////////////////////////////////////////////////////////////////////




    func peripheral(_ peripheral: CBPeripheral, didWriteValueFor characteristic: CBCharacteristic, error: Error?) {
        if let error = error {
            print("❌ Error writing characteristic: \(error.localizedDescription)")
        } else {
            print("✅ Successfully wrote to characteristic: \(characteristic.uuid)")
        }
    }
    // เพิ่ม method สำหรับดึงข้อมูลอุปกรณ์แบบละเอียด
    @objc func getDetailedDeviceInfo(for uuidString: String) -> NSDictionary {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            return [:]
        }
        
        var deviceInfo: [String: Any] = [
            "name": peripheral.name ?? "Unknown",
            "uuid": uuidString,
            "rssi": _rssi,
            "major": _major,
            "minor": _minor,
            "state": connectionStateString(peripheral.state),
            "timestamp": Date().timeIntervalSince1970
        ]
        
        // เพิ่มข้อมูล services
        if let services = connectedServices[uuid] {
            let serviceInfo = services.map { service in
                return [
                    "uuid": service.uuid.uuidString,
                    "isPrimary": service.isPrimary
                ]
            }
            deviceInfo["services"] = serviceInfo
        }
        
        // เพิ่มข้อมูล characteristics
        if let characteristics = availableCharacteristics[uuid] {
            let charInfo = characteristics.map { char in
                return [
                    "uuid": char.uuid.uuidString,
                    "properties": characteristicPropertiesString(char.properties),
                    "value": char.value?.base64EncodedString() ?? ""
                ]
            }
            deviceInfo["characteristics"] = charInfo
        }
        
        return deviceInfo as NSDictionary
    }

    private func connectionStateString(_ state: CBPeripheralState) -> String {
        switch state {
        case .disconnected: return "disconnected"
        case .connecting: return "connecting"
        case .connected: return "connected"
        case .disconnecting: return "disconnecting"
        @unknown default: return "unknown"
        }
    }

    private func characteristicPropertiesString(_ properties: CBCharacteristicProperties) -> [String] {
        var props: [String] = []
        if properties.contains(.read) { props.append("read") }
        if properties.contains(.write) { props.append("write") }
        if properties.contains(.writeWithoutResponse) { props.append("writeWithoutResponse") }
        if properties.contains(.notify) { props.append("notify") }
        if properties.contains(.indicate) { props.append("indicate") }
        return props
    }

    private func updateCharacteristicData(peripheral: CBPeripheral, characteristic: CBCharacteristic, data: Data) {
        // ****อัพเดทข้อมูลใน delbck*****
        let deviceInfo = [
            "deviceUUID": peripheral.identifier.uuidString,
            "deviceName": peripheral.name ?? "Unknown",
            "characteristicUUID": characteristic.uuid.uuidString,
            "data": data.base64EncodedString(),
            "timestamp": Date().timeIntervalSince1970
        ] as [String : Any]
        
        // ส่งข้อมูลไปยัง delegate หรือ notification
        print("📊 Updated characteristic data: \(deviceInfo)")
    }
    // เพิ่ม methods สำหรับจัดการสถานะการเชื่อมต่อ
    @objc func getConnectionState(_ uuidString: String) -> String {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            print("❌ Peripheral not found for connection state: \(uuidString)")
            return "unknown"
        }
        
        let state = connectionStateString(peripheral.state)
        print("📱 Connection state for \(peripheral.name ?? "Unknown"): \(state)")
        return state
    }

    @objc func isDeviceConnected(_ uuidString: String) -> Bool {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid] else {
            return false
        }
        
        return peripheral.state == .connected
    }

    @objc(getAvailableServices:)
    func getAvailableServices(_ uuidString: String) -> [String] {
        guard let uuid = UUID(uuidString: uuidString),
              let services = connectedServices[uuid] else {
            print("❌ No services found for device: \(uuidString)")
            return []  // ✅ Return empty String array
        }
        
        // ✅ Return array of service UUIDs as strings
        let serviceUUIDs = services.map { $0.uuid.uuidString }
        print("📋 Available services: \(serviceUUIDs)")
        return serviceUUIDs
    }

    // ✅ เพิ่ม method สำหรับ detailed info
    @objc(getAvailableServicesWithNames:)
    func getAvailableServicesWithNames(_ uuidString: String) -> [String] {
        guard let uuid = UUID(uuidString: uuidString),
              let services = connectedServices[uuid] else {
            print("❌ No services found for device: \(uuidString)")
            return []
        }
        
        // ✅ Return array of "Name (UUID)" strings
        let serviceStrings = services.map { service in
            let name = getServiceName(for: service.uuid)
            let uuid = service.uuid.uuidString
            return "\(name) (\(uuid))"
        }
        
        print("📋 Available services with names: \(serviceStrings)")
        return serviceStrings
    }

    // @objc(getDetailedDeviceInfo:)
    // func getDetailedDeviceInfo(_ uuidString: String) -> NSDictionary {
    //     guard let uuid = UUID(uuidString: uuidString),
    //           let peripheral = discoveredPeripherals[uuid] else {
    //         print("❌ Device not found for detailed info: \(uuidString)")
    //         return [:]
    //     }
        
    //     // เพิ่มข้อมูล services
    //     if let services = connectedServices[uuid] {
    //         let serviceInfo = services.map { service -> NSDictionary in
    //             return [
    //                 "uuid": service.uuid.uuidString,
    //                 "name": getServiceName(for: service.uuid),
    //                 "isPrimary": service.isPrimary
    //             ] as NSDictionary
    //         }
    //         deviceInfo["services"] = serviceInfo
    //         deviceInfo["serviceCount"] = services.count
    //     } else {
    //         deviceInfo["services"] = []
    //         deviceInfo["serviceCount"] = 0
    //     }
        
    //     // เพิ่มข้อมูล characteristics
    //     if let characteristics = availableCharacteristics[uuid] {
    //         let charInfo = characteristics.map { char -> NSDictionary in
    //             return [
    //                 "uuid": char.uuid.uuidString,
    //                 "name": getCharacteristicName(for: char.uuid),
    //                 "properties": characteristicPropertiesString(char.properties),
    //                 "value": char.value?.base64EncodedString() ?? ""
    //             ] as NSDictionary
    //         }
    //         deviceInfo["characteristics"] = charInfo
    //         deviceInfo["characteristicCount"] = characteristics.count
    //     } else {
    //         deviceInfo["characteristics"] = []
    //         deviceInfo["characteristicCount"] = 0
    //     }
        
    //     print("📊 Detailed device info prepared for: \(peripheral.name ?? "Unknown")")
    //     return deviceInfo as NSDictionary
    // }

    // ✅ เพิ่มใน BluetoothManager class ก่อน closing brace สุดท้าย

// MARK: - Battery Management Functions
func updateBatteryInfo(level: Int, deviceUUID: String, deviceName: String) {
    batteryInfo = [
        "level": level,
        "deviceUUID": deviceUUID,
        "deviceName": deviceName,
        "timestamp": Date().timeIntervalSince1970,
        "status": getBatteryStatus(level: level),
        "icon": getBatteryIcon(level: level)
    ]
    
    print("🔋 Battery Info Updated: \(batteryInfo)")
    
    // อัพเดท UI ด้วยข้อมูลแบตเตอรี่
    updateUIWithBattery(name: deviceName, rssi: _rssi, batteryLevel: level)
}

func getBatteryStatus(level: Int) -> String {
    switch level {
    case 81...100: return "Excellent"
    case 61...80: return "Good"
    case 41...60: return "Fair"
    case 21...40: return "Low"
    case 1...20: return "Critical"
    case 0: return "Empty"
    default: return "Unknown"
    }
}

func getBatteryIcon(level: Int) -> String {
    switch level {
    case 81...100: return "🟢"  // เขียว - ดีมาก
    case 61...80: return "🟡"   // เหลือง - ดี
    case 41...60: return "🟠"   // ส้ม - ปานกลาง
    case 21...40: return "🔴"   // แดง - ต่ำ
    case 1...20: return "🚨"    // วิกฤต
    case 0: return "⚫"         // หมด
    default: return "❓"        // ไม่ทราบ
    }
}

// อัพเดท UI method ให้รวมแบตเตอรี่
@objc(updateUIWithBatteryName:rssi:batteryLevel:)
func updateUIWithBattery(name: String, rssi: Int, batteryLevel: Int) {
    _rssi = rssi
    _name = name
    
    let batteryIcon = getBatteryIcon(level: batteryLevel)
    let batteryStatus = getBatteryStatus(level: batteryLevel)
    
    let scannedInfo = """
    \(name), RSSI: \(rssi) dBm
    UUID: \(_uuid)
    Major: \(_major), Minor: \(_minor)
    🔋 Battery: \(batteryLevel)% \(batteryIcon) (\(batteryStatus))
    """
    
    print("Swift updateUI with Battery called:")
    print("Name: \(name)")
    print("RSSI: \(rssi)")
    print("Battery: \(batteryLevel)% (\(batteryStatus))")
    print("UUID: \(_uuid)")
    print("Major: \(_major), Minor: \(_minor)")
    print("Scanned Info: \(scannedInfo)")
}

// MARK: - Battery Access Methods for Python
@objc func getCurrentBatteryInfo() -> NSDictionary {
    print("getCurrentBatteryInfo called, returning: \(batteryInfo)")
    return batteryInfo as NSDictionary
}

@objc(getBatteryLevelForDevice:)
func getBatteryLevelForDevice(_ uuidString: String) -> Int {
    if let level = batteryInfo["level"] as? Int,
       let deviceUUID = batteryInfo["deviceUUID"] as? String,
       deviceUUID == uuidString {
        print("Battery level for \(uuidString): \(level)%")
        return level
    }
    print("No battery info found for device: \(uuidString)")
    return -1 // ไม่พบข้อมูล
}

@objc(requestBatteryUpdateForDevice:)
func requestBatteryUpdate(uuidString: String) {
    print("Requesting battery update for device: \(uuidString)")
    
    guard let uuid = UUID(uuidString: uuidString),
          let peripheral = discoveredPeripherals[uuid],
          peripheral.state == .connected else {
        print("❌ Device not connected for battery update")
        return
    }
    
    // หา Battery Service และ Battery Level Characteristic
    if let services = peripheral.services {
        for service in services {
            if service.uuid.uuidString == "180F" {  // Battery Service
                if let characteristics = service.characteristics {
                    for characteristic in characteristics {
                        if characteristic.uuid.uuidString == "2A19" {  // Battery Level
                            print("📖 Reading battery level...")
                            peripheral.readValue(for: characteristic)
                            return
                        }
                    }
                }
            }
        }
    }
    
    print("❌ Battery service/characteristic not found")
}




// เพิ่ม method สำหรับ get ข้อมูลแบตเตอรี่แบบละเอียด
@objc func getDetailedBatteryInfo() -> NSDictionary {
    var detailedInfo = batteryInfo
    
    if let level = batteryInfo["level"] as? Int {
        detailedInfo["percentage"] = level
        detailedInfo["isLow"] = level <= 20
        detailedInfo["isCritical"] = level <= 10
        detailedInfo["isCharging"] = false  // ไม่สามารถตรวจสอบได้จาก BLE
        detailedInfo["estimatedHours"] = estimateBatteryHours(level: level)
    }
    
    return detailedInfo as NSDictionary
}

func estimateBatteryHours(level: Int) -> Double {
    // ประมาณการเวลาที่เหลือ (สมมติ)
    switch level {
    case 81...100: return Double(level - 80) * 0.5 + 8.0  // 8-18 ชั่วโมง
    case 61...80: return Double(level - 60) * 0.3 + 4.0   // 4-10 ชั่วโมง
    case 41...60: return Double(level - 40) * 0.15 + 1.0  // 1-4 ชั่วโมง
    case 21...40: return Double(level - 20) * 0.05 + 0.2  // 0.2-1.2 ชั่วโมง
    case 1...20: return Double(level) * 0.01              // 0.01-0.2 ชั่วโมง
    default: return 0.0
    }
}

// เพิ่ม Device Model helper function ถ้ายังไม่มี
func getDeviceModel(identifier: String) -> String {
    switch identifier {
    case "iPhone12,1": return "iPhone 11"
    case "iPhone12,3": return "iPhone 11 Pro"
    case "iPhone12,5": return "iPhone 11 Pro Max"
    case "iPhone12,8": return "iPhone SE (2nd generation)"
    case "iPhone13,1": return "iPhone 12 mini"
    case "iPhone13,2": return "iPhone 12"
    case "iPhone13,3": return "iPhone 12 Pro"
    case "iPhone13,4": return "iPhone 12 Pro Max"
    case "iPhone14,4": return "iPhone 13 mini"
    case "iPhone14,5": return "iPhone 13"
    case "iPhone14,2": return "iPhone 13 Pro"
    case "iPhone14,3": return "iPhone 13 Pro Max"
    case "iPhone14,6": return "iPhone SE (3rd generation)"
    case "iPhone14,7": return "iPhone 14"
    case "iPhone14,8": return "iPhone 14 Plus"
    case "iPhone15,2": return "iPhone 14 Pro"
    case "iPhone15,3": return "iPhone 14 Pro Max"
    case "iPhone15,4": return "iPhone 15"
    case "iPhone15,5": return "iPhone 15 Plus"
    case "iPhone16,1": return "iPhone 15 Pro"
    case "iPhone16,2": return "iPhone 15 Pro Max"
    default: return identifier
    }
}

// เพิ่ม Characteristic name helper ถ้ายังไม่มี
func getCharacteristicName(for uuid: CBUUID) -> String {
    switch uuid.uuidString {
    case "2A19": return "Battery Level"
    case "2A29": return "Manufacturer Name String"
    case "2A24": return "Model Number String"
    case "2A2B": return "Current Time"
    case "2A0F": return "Local Time Information"
    default: return uuid.uuidString
    }
}

// เพิ่ม Service name helper ถ้ายังไม่มี
func getServiceName(for uuid: CBUUID) -> String {
    switch uuid.uuidString {
    case "180F": return "Battery"
    case "180A": return "Device Information"
    case "1805": return "Current Time"
    case "D0611E78-BBB4-4591-A5F8-487910AE4366": return "Continuity"
    default: return uuid.uuidString
    }
}

func peripheral(_ peripheral: CBPeripheral, didReadRSSI RSSI: NSNumber, error: Error?) {
     guard error == nil else {
        print("❌ Error reading RSSI: \(error!.localizedDescription)")
        return
     }
        
        let rssiValue = RSSI.intValue
        let deviceName = peripheral.name ?? "Unknown"
        let deviceUUID = peripheral.identifier.uuidString
        
        // ✅ เช็คการเปลี่ยนแปลงใน Swift ด้วย
        let oldRSSI = _rssi
        
        print("📶 RSSI Read Complete:")
        print("   Device: \(deviceName)")
        print("   Old RSSI: \(oldRSSI)")
        print("   New RSSI: \(rssiValue)")
        print("   Changed: \(oldRSSI != rssiValue)")
        
        // อัพเดท internal state
        _rssi = rssiValue
        _name = deviceName
        _uuid = deviceUUID
        
        // อัพเดท device info
        setDeviceInfo(uuid: deviceUUID, major: _major, minor: _minor, rssi: rssiValue, name: deviceName)
        
        print("✅ RSSI updated in Swift: \(_rssi)")
    }

    // เพิ่ม properties สำหรับ timer
    private var rssiTimer: Timer?
    private var monitoringPeripheral: CBPeripheral?

    @objc(startPeriodicRSSIUpdates:interval:)
    func startPeriodicRSSIUpdates(uuidString: String, interval: TimeInterval = 2.0) {
        guard let uuid = UUID(uuidString: uuidString),
              let peripheral = discoveredPeripherals[uuid],
              peripheral.state == .connected else {
            print("❌ Device not connected for periodic RSSI updates")
            return
        }
        print("ttttt")
        
        // หยุด timer เก่า (ถ้ามี)
        stopPeriodicRSSIUpdates()
        
        monitoringPeripheral = peripheral
        peripheral.delegate = self
        
        // สร้าง timer สำหรับอ่าน RSSI ทุก 2 วินาที
        rssiTimer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { [weak self] _ in
            guard let self = self, 
                  let peripheral = self.monitoringPeripheral,
                  peripheral.state == .connected else {
                self?.stopPeriodicRSSIUpdates()
                return
            }
            
            peripheral.readRSSI()
            print("🔄 Periodic RSSI read requested")
        }
        
        // อ่านครั้งแรกทันที
        peripheral.readRSSI()
        
        print("✅ Started periodic RSSI updates every \(interval) seconds for: \(peripheral.name ?? "Unknown")")
    }

    @objc func stopPeriodicRSSIUpdates() {
        rssiTimer?.invalidate()
        rssiTimer = nil
        monitoringPeripheral = nil
        print("⏹️ Stopped periodic RSSI updates")
    }

    // เพิ่ม method นี้ใน BluetoothManager class
    @objc(stopPeriodicRSSIUpdatesForDevice:)
    func stopPeriodicRSSIUpdatesForDevice(uuid: String) {
        print("BluetoothManager: Stopping periodic RSSI updates for device: \(uuid)")
        
        if uuid.isEmpty {
            print("❌ Invalid UUID for stopping RSSI updates")
            return
        }
        
        // หยุด timer ถ้ามี
        if let timer = rssiTimer {
            timer.invalidate()
            rssiTimer = nil
            print("⏹️ RSSI Timer stopped")
        }
        
        // ล้าง monitoring peripheral
        monitoringPeripheral = nil
        
        print("✅ Stopped periodic RSSI updates for device: \(uuid)")
    }
 




    let locationManager = CLLocationManager()

    // MARK: - Beacon Region Config (UUID + Major)
    let regions: [CLBeaconRegion] = [ // กำหนดรายการของ Beacon ที่ต้องการสแกนไว้ มีทั้งหมด 8 region ที่ต่างกัน 
        CLBeaconRegion(uuid: UUID(uuidString: "a1111111-1111-1111-1111-111111111111")!, major: 111, identifier: "A-111"),
        CLBeaconRegion(uuid: UUID(uuidString: "a1111111-1111-1111-1111-111111111111")!, major: 888, identifier: "A-888"),

        CLBeaconRegion(uuid: UUID(uuidString: "b2222222-2222-2222-2222-222222222222")!, major: 111, identifier: "B-111"),
        CLBeaconRegion(uuid: UUID(uuidString: "b2222222-2222-2222-2222-222222222222")!, major: 888, identifier: "B-888"),

        CLBeaconRegion(uuid: UUID(uuidString: "c3333333-3333-3333-3333-333333333333")!, major: 111, identifier: "C-111"),
        CLBeaconRegion(uuid: UUID(uuidString: "c3333333-3333-3333-3333-333333333333")!, major: 888, identifier: "C-888"),

        CLBeaconRegion(uuid: UUID(uuidString: "d4444444-4444-4444-4444-444444444444")!, major: 111, identifier: "D-111"),
        CLBeaconRegion(uuid: UUID(uuidString: "d4444444-4444-4444-4444-444444444444")!, major: 888, identifier: "D-888")
    ]// นี่คือค่าที่่ประกาศตัวเเปรไว้ ทั้ง 8 ค่า 

    func startScanning() {
        print("✅ start periodic RSSI updates for device:") // เพื่อเริ่มตรวจจับการเข้า/ออกแต่ละ region เพื่ออ่าน RSSI และข้อมูลจาก Beacon ภายใน region
        for region in regions {
            region.notifyEntryStateOnDisplay = true
            locationManager.startMonitoring(for: region)
            locationManager.startRangingBeacons(satisfying: CLBeaconIdentityConstraint(uuid: region.uuid, major: CLBeaconMajorValue(region.major!)))
        }
        
    }

    func stopScanning() { // หยุดการสแกนทั้งหมด
        print("🛑 stop scanning for beacons")
        for region in regions {
            locationManager.stopMonitoring(for: region)
            locationManager.stopRangingBeacons(satisfying: CLBeaconIdentityConstraint(uuid: region.uuid, major: CLBeaconMajorValue(region.major!)))
    }
}
    private var latestBeaconData: [String: Any] = [:]
    private var allBeacons: [[String: Any]] = []
    private var uuid_beacon: String = ""
    private var _proximity: String = ""
    private var name_beacon: String = ""
    private var rssi_beacon: String = ""
    private var major_beacon: String = ""
    private var minor_beacon: String = ""
    // ใช้สำหรับเก็บข้อมูล Beacon ที่ตรวจพบล่าสุด หรือทั้งหมด

    
    @objc protocol BeaconRangeDelegate { // คือ Protocol สำหรับส่งข้อมูล beacon ที่สแกนได้ ไปยัง delegate
    func didRangeBeacons(beacons: [[String: Any]]) // ส่งข้อมูล beacon ทั้งหมดที่เจอแบบ array
    func didUpdateBeacon(uuid: String, major: Int, minor: Int, rssi: Int) // ส่งข้อมูล beacon เฉพาะตัวเดียวล่าสุด
}
    // MARK: - เก็บ Beacon ที่เคยเจอแล้ว (ไม่ซ้ำ)
var seenBeacons: Set<String> = []

func locationManager(_ manager: CLLocationManager, didRange beacons: [CLBeacon], satisfying beaconConstraint: CLBeaconIdentityConstraint) { // ทำการ ranging แล้วพบ Beacon ภายในช่วงสัญญาณ (ระยะใกล้พอ)
    var beaconDataArray: [[String: Any]] = [] // เตรียม array เพื่อเก็บข้อมูล Beacon ทุกตัวที่เจอ
    for beacon in beacons { // วนลูปผ่าน Beacon ที่อยู่ในช่วงสัญญาณ

        let uuid_ = beacon.uuid
        let major = beacon.major.intValue
        let minor = beacon.minor.intValue
        let rssi = beacon.rssi
        let proximity = proximityString(beacon.proximity)
        let accuracy = beacon.accuracy
        // ดึงข้อมูลจาก CLBeacon แต่ละตัว เช่น UUID, major, minor, RSSI, proximity และระยะประมาณ (accuracy)

        let beaconKey = "\(uuid_.uuidString)_\(major)_\(minor)" //สร้าง “key” ที่ใช้ระบุ beacon เฉพาะ major และ minor เท่านั้น

        if seenBeacons.contains(beaconKey) {
            print("⏩ Already processed: \(beaconKey), stopping scan...")

            manager.stopRangingBeacons(satisfying: beaconConstraint)
            break
        } // 🛑 หยุดการสแกนทันทีเมื่อเจอ beacon ซ้ำ
                
        seenBeacons.insert(beaconKey) // เก็บ beaconKey นี้ไว้ในชุดข้อมูลที่เคยเจอแล้ว

        let beaconData: [String: Any] = [
            "uuid": uuid_.uuidString,
            "major": major,
            "minor": minor,
            "rssi": rssi,
            "timestamp": Date().timeIntervalSince1970,
            "proximity": proximity,
            "accuracy": accuracy
        ] // รวมข้อมูล beacon แต่ละตัวไว้ใน dictionary (beaconData) เพื่อนำไปใช้งาน

        beaconDataArray.append(beaconData) // insert ข้อมูลลงใน array เพื่อเก็บข้อมูล Beacon ทั้งหมดที่เจอ

        print("📡 NEW Beacon: \(beaconKey), RSSI: \(rssi)")
        print("DataArray.append")
        print(beaconDataArray)
    } // แสดงข้อมูล
}


    private func proximityString(_ proximity: CLProximity) -> String {
        switch proximity {
        case .immediate: return "immediate"
        case .near: return "near"
        case .far: return "far"
        case .unknown: return "unknown"
        @unknown default: return "unknown"
    } // ต้องการแสดงหรือส่งค่า proximity ในรูปแบบข้อความ
}

    // MARK: - Delegate: Authorization
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        if manager.authorizationStatus == .authorizedWhenInUse || manager.authorizationStatus == .authorizedAlways {
            
        } // ตรวจสอบว่าผู้ใช้ให้อนุญาตใช้ location หรือไม่
    }

    // เพิ่ม methods เหล่านี้ใน BluetoothManager class

    @objc func getBeaconRegions() -> [[String: Any]] { // ใช้สำหรับตรวจสอบว่าแอปกำลัง monitor beacons ใด
        var regionsData: [[String: Any]] = []
        
        for region in regions {
            let regionInfo: [String: Any] = [
                "uuid": region.uuid.uuidString,
                "major": region.major?.intValue ?? 0,
                "identifier": region.identifier
            ]
            regionsData.append(regionInfo)
        }
        
        return regionsData
    }

    @objc func getBeaconRegionsAsJSON() -> String { // คืนค่ารูปแบบ JSON (string) ของ regions ทั้งหมด
        let regionsData = getBeaconRegions()
        
        do {
            let jsonData = try JSONSerialization.data(withJSONObject: regionsData, options: .prettyPrinted)
            return String(data: jsonData, encoding: .utf8) ?? "[]"
        } catch {
            print("Error converting beacon regions to JSON: \(error)")
            return "[]"
        }
    }

    @objc func getBeaconRegionByIdentifier(_ identifier: String) -> [String: Any]? { // รับ identifier แล้วคืนค่าข้อมูลของ region ที่มี identifier นั้น
        for region in regions {
            if region.identifier == identifier {
                return [
                    "uuid": region.uuid.uuidString,
                    "major": region.major?.intValue ?? 0,
                    "identifier": region.identifier
                ]
            }
        }
        return nil
    }

    @objc func getAllBeaconUUIDs() -> [String] { // คืนค่า array ของ UUID beacon ที่ใช้อยู่ทั้งหมดใน regions
        return regions.map { $0.uuid.uuidString }
    }

    @objc func getBeaconRegionsCount() -> Int { // คืนจำนวน regions ที่กำลัง monitor อยู่
        return regions.count
    }
    @objc func getbe() -> NSDictionary { // คืนค่า beacon ล่าสุดที่เจอ โดยดึงจากตัวแปร name, uuid, rssi, major, minor, proximity
        return [
            "name": name_beacon,
            "uuid": uuid_beacon,
            "rssi": rssi_beacon,
            "major": major_beacon,
            "minor": minor_beacon,
            "proximity": _proximity,
        ]
    }
} // ← closing brace ของ BluetoothManager class

@objc protocol BluetoothBridgeDelegate {
    @objc optional func didConnectToDevice(uuid: String)
    @objc optional func didDisconnectFromDevice(uuid: String, error: Error?)
    @objc optional func didFailToConnectToDevice(uuid: String, error: Error?)
}
