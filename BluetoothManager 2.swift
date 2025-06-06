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
    //////////
    var disconnectedPeripherals: [UUID: CBPeripheral] = [:] // เก็บ peripheral ที่ disconnect แล้ว
    private var _autoReconnect: Bool = false // เปลี่ยนเป็น private
    var maxReconnectAttempts: Int = 3
    var reconnectAttempts: [UUID: Int] = [:]
///////////
    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
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
            if currentAttempts < maxReconnectAttempts {
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
        if currentAttempts >= maxReconnectAttempts {
            print("Max reconnect attempts reached for device: \(uuidString)")
            return
        }
        
        // เพิ่ม attempt count
        reconnectAttempts[uuid] = currentAttempts + 1
        
        // ทำการ reconnect
        centralManager?.connect(targetPeripheral, options: nil)
        print("Reconnection attempt \(currentAttempts + 1)/\(maxReconnectAttempts) for device: \(targetPeripheral.name ?? "Unknown")")
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
        maxReconnectAttempts = attempts
        print("Max reconnect attempts set to: \(attempts)")
    }

    @objc var isAutoReconnectEnabled: Bool {
        return _autoReconnect
    }

    @objc func getConnectedPeripheralsCount() -> Int {
        let connectedPeripherals = centralManager?.retrieveConnectedPeripherals(withServices: []) ?? []
        return connectedPeripherals.count
    }
}

@objc protocol BluetoothBridgeDelegate {
    @objc optional func didConnectToDevice(uuid: String)
    @objc optional func didDisconnectFromDevice(uuid: String, error: Error?)
    @objc optional func didFailToConnectToDevice(uuid: String, error: Error?)
}
/////////////////////////
