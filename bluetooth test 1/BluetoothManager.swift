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
                // iBeacon format: bytes 20-21: major, 22-23: minor
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
        peripheral.delegate = self
        peripheral.discoverServices(nil)  // optional: for characteristic discovery
    }

}
