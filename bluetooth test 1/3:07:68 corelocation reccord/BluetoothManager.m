  #import "flask-Bridging-Header.h"
  #import "flask-Swift.h"  // Replace with your actual Swift header name

  @interface BluetoothBridge () <BluetoothScanDelegate>
  @property (nonatomic, strong) BluetoothManager *manager;
  @property (nonatomic, strong) NSDictionary *lastDevice;
  @property (nonatomic, strong) NSMutableArray *discoveredDevices;
  @property (nonatomic, strong) NSMutableArray *connectedDevices;
  @property (nonatomic, assign) BOOL isCurrentlyScanning;


  @property (nonatomic, strong) NSDictionary *latestBeaconData;
  @property (nonatomic, strong) NSArray *allBeaconData;
  @property (nonatomic, copy) void (^beaconUpdateBlock)(NSString *uuid, NSInteger major, NSInteger minor, NSInteger rssi);
  @end

  @implementation BluetoothBridge

  - (instancetype)init {
      self = [super init];
      if (self) {
          _manager = [[BluetoothManager alloc] init];
          _manager.delegate = self;
          _discoveredDevices = [[NSMutableArray alloc] init];
          _connectedDevices = [[NSMutableArray alloc] init];
          _isCurrentlyScanning = NO;
          NSLog(@"BluetoothBridge initialized with manager: %@", _manager);
    
      }
      return self;
  }

  #pragma mark - Basic Scanning Methods

  - (void)startBluetoothScan {
      NSLog(@"BluetoothBridge: Starting scan...");
      [_discoveredDevices removeAllObjects];
      _isCurrentlyScanning = YES;
      [_manager startScan];
  }

  - (void)stopBluetoothScan {
      NSLog(@"BluetoothBridge: Stopping scan...");
      _isCurrentlyScanning = NO;
      [_manager stopScan];
    
      // เพิ่ม: Clear last device data เมื่อหยุด scan
      self.lastDevice = nil;
    
      NSLog(@"BluetoothBridge: Scan stopped and device data cleared");
  }

  #pragma mark - Connection Methods

  - (void)connectToDeviceWithUUID:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Connecting to device with UUID: %@", uuid);
      [_manager connectToPeripheralWith:uuid];
  }

  - (void)disconnectFromDeviceWithUUID:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Disconnecting from device with UUID: %@", uuid);
      [_manager disconnectPeripheralWith:uuid];
  }

  - (void)reconnectToDeviceWithUUID:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Reconnecting to device with UUID: %@", uuid);
      [_manager reconnectToPeripheralWith:uuid];
  }

  #pragma mark - Configuration Methods

  - (void)setAutoReconnectEnabled:(BOOL)enabled {
      NSLog(@"BluetoothBridge: Setting auto-reconnect to: %@", enabled ? @"YES" : @"NO");
      [_manager setAutoReconnect:enabled];
  }

  - (void)setMaxReconnectAttempts:(NSInteger)attempts {
      NSLog(@"BluetoothBridge: Setting max reconnect attempts to: %ld", (long)attempts);
      [_manager configureMaxReconnectAttempts:(int)attempts];  // เปลี่ยนจาก setMaxReconnectAttempts
  }

  - (void)setupAutoReconnectHandler {
      [_manager setAutoReconnectHandler:^(NSString *uuid) {
          dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(2.0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
              [self->_manager reconnectToPeripheralWith:uuid];
          });
      }];
  }

  #pragma mark - BluetoothScanDelegate Methods

  - (void)didDiscoverDeviceWithName:(NSString *)name
                             uuid:(NSString *)uuid
                             rssi:(NSInteger)rssi
                              major:(NSInteger)major
                              minor:(NSInteger)minor {
    
      NSLog(@"BluetoothBridge: Device discovered - Name: %@, UUID: %@, RSSI: %ld, Major: %ld, Minor: %ld",
            name, uuid, (long)rssi, (long)major, (long)minor);
    
      NSDictionary *deviceInfo = @{
          @"name": name ?: @"Unknown",
          @"uuid": uuid ?: @"",
          @"rssi": @(rssi),
          @"major": @(major),
          @"minor": @(minor),
          @"timestamp": @([[NSDate date] timeIntervalSince1970])
      };
    
      self.lastDevice = deviceInfo;
    
      // Check if device already exists in discovered devices
      BOOL deviceExists = NO;
      for (NSMutableDictionary *existingDevice in _discoveredDevices) {
          if ([existingDevice[@"uuid"] isEqualToString:uuid]) {
              // Update existing device info
              [existingDevice setValuesForKeysWithDictionary:deviceInfo];
              deviceExists = YES;
              break;
          }
      }
      
    
      if (!deviceExists) {
          [_discoveredDevices addObject:[deviceInfo mutableCopy]];
      }
    
      NSLog(@"BluetoothBridge: Total discovered devices: %lu", (unsigned long)[_discoveredDevices count]);
  }

  - (void)didConnectToDeviceWithUUID:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Successfully connected to device: %@", uuid);
    
      // Find device in discovered devices and add to connected devices
      for (NSDictionary *device in _discoveredDevices) {
          if ([device[@"uuid"] isEqualToString:uuid]) {
              NSMutableDictionary *connectedDevice = [device mutableCopy];
              connectedDevice[@"connectionStatus"] = @"connected";
              connectedDevice[@"connectedTimestamp"] = @([[NSDate date] timeIntervalSince1970]);
            
              // Remove if already exists in connected devices
              [_connectedDevices removeObject:connectedDevice];
              [_connectedDevices addObject:connectedDevice];
              break;
          }
      }
    
      NSLog(@"BluetoothBridge: Total connected devices: %lu", (unsigned long)[_connectedDevices count]);
  }

  - (void)didDisconnectFromDeviceWithUUID:(NSString *)uuid error:(NSError *)error {
      NSString *errorMessage = error ? error.localizedDescription : @"No error";
      NSLog(@"BluetoothBridge: Disconnected from device: %@ with error: %@", uuid, errorMessage);
    
      // Remove from connected devices
      NSMutableArray *devicesToRemove = [[NSMutableArray alloc] init];
      for (NSDictionary *device in _connectedDevices) {
          if ([device[@"uuid"] isEqualToString:uuid]) {
              [devicesToRemove addObject:device];
          }
      }
      [_connectedDevices removeObjectsInArray:devicesToRemove];
    
      NSLog(@"BluetoothBridge: Total connected devices: %lu", (unsigned long)[_connectedDevices count]);
  }

  - (void)didFailToConnectToDeviceWithUUID:(NSString *)uuid error:(NSError *)error {
      NSString *errorMessage = error ? error.localizedDescription : @"Unknown connection error";
      NSLog(@"BluetoothBridge: Failed to connect to device: %@ with error: %@", uuid, errorMessage);
  }

  #pragma mark - Data Retrieval Methods

  - (NSDictionary *)getLastDiscoveredDevice {
      // ถ้าไม่ได้ scan อยู่ ให้คืน nil หรือ empty
      if (!_isCurrentlyScanning) {
          NSLog(@"BluetoothBridge: Not scanning, returning nil");
          return nil;
      }
    
      NSLog(@"BluetoothBridge: getLastDiscoveredDevice called, returning: %@", self.lastDevice);
      return self.lastDevice;
  }

  - (NSArray *)getAllDiscoveredDevices {
      NSLog(@"BluetoothBridge: getAllDiscoveredDevices called, returning %lu devices", 
            (unsigned long)[_discoveredDevices count]);
      return [_discoveredDevices copy];
  }

  - (NSArray *)getConnectedDevices {
      NSLog(@"BluetoothBridge: getConnectedDevices called, returning %lu devices", 
            (unsigned long)[_connectedDevices count]);
      return [_connectedDevices copy];
  }

  - (NSInteger)getConnectedDevicesCount {
      NSLog(@"BluetoothBridge: Getting connected devices count");
      return [_manager getConnectedPeripheralsCount];
  }

  #pragma mark - Status Methods

  - (BOOL)isScanning {
      return _isCurrentlyScanning;
  }

  - (BOOL)isBluetoothEnabled {
      // This would need to be implemented in BluetoothManager to check CBCentralManager state
      return YES; // Placeholder
  }

  - (NSString *)getBluetoothState {
      // This would need to be implemented in BluetoothManager to return actual state
      return @"poweredOn"; // Placeholder
  }

  #pragma mark - Helper Methods for Python Integration

  - (NSDictionary *)getDeviceInfoByUUID:(NSString *)uuid {
      for (NSDictionary *device in _discoveredDevices) {
          if ([device[@"uuid"] isEqualToString:uuid]) {
              return device;
          }
      }
      return nil;
  }

  - (NSString *)getDevicesAsJSONString {
      NSError *error;
      NSData *jsonData = [NSJSONSerialization dataWithJSONObject:_discoveredDevices
                                                       options:NSJSONWritingPrettyPrinted
                                                         error:&error];
      if (error) {
          NSLog(@"Error converting devices to JSON: %@", error.localizedDescription);
          return @"[]";
      }
    
      return [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
  }

  - (NSString *)getConnectedDevicesAsJSONString {
      NSError *error;
      NSData *jsonData = [NSJSONSerialization dataWithJSONObject:_connectedDevices
                                                       options:NSJSONWritingPrettyPrinted
                                                         error:&error];
      if (error) {
          NSLog(@"Error converting connected devices to JSON: %@", error.localizedDescription);
          return @"[]";
      }
    
      return [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
  }

  // เพิ่ม method สำหรับ RSSI monitoring
  - (void)startRSSIUpdatesForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Starting RSSI updates for device: %@", uuid);
      if (uuid && [uuid length] > 0) {
          [_manager startRSSIUpdatesForPeripheral:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for RSSI updates");
      }
  }

  - (void)stopRSSIUpdatesForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Stopping RSSI updates for device: %@", uuid);
      if (uuid && [uuid length] > 0) {
          [_manager stopRSSIUpdatesForPeripheral:uuid];
      }
  }

  - (NSInteger)getCurrentRSSIForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Getting current RSSI for device: %@", uuid);
      if (uuid && [uuid length] > 0) {
          return [_manager getCurrentRSSIForPeripheral:uuid];
      }
      return -999; // Error value
  }

  // เพิ่ม method สำหรับดึงข้อมูล device ปัจจุบัน
  - (NSDictionary *)getCurrentDeviceInfo {
      NSLog(@"BluetoothBridge: Getting current device info");
      return [_manager getCurrentDeviceInfo];
  }
-(NSDictionary *)getbe{
    NSLog(@"getbe");
    return [_manager getbe];
}

  // เพิ่ม method นี้ใน BluetoothBridge implementation
  - (void)clearDiscoveredDevices {
      NSLog(@"BluetoothBridge: Clearing all discovered device data");
      [_discoveredDevices removeAllObjects];
      [_connectedDevices removeAllObjects];
      self.lastDevice = nil;
      NSLog(@"BluetoothBridge: Device data cleared successfully");
  }

  #pragma mark - GATT Connection Methods

  - (void)startConnectionForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Starting GATT connection for device: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          [_manager connectToPeripheralWith:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for GATT connection");
      }
  }

  - (void)startPeriodicRSSIUpdatesForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Starting periodic RSSI updates for device: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          [_manager startRSSIUpdatesForPeripheral:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for periodic RSSI updates");
      }
  }

  - (void)stopPeriodicRSSIUpdatesForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Stopping periodic RSSI updates for device: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          [_manager stopPeriodicRSSIUpdatesForDevice:uuid];
      }
  }

  #pragma mark - GATT Service and Characteristic Methods

  - (void)readCharacteristicForDevice:(NSString *)deviceUUID 
                        serviceUUID:(NSString *)serviceUUID 
                 characteristicUUID:(NSString *)characteristicUUID {
      NSLog(@"BluetoothBridge: Reading characteristic %@ from service %@ on device %@", 
            characteristicUUID, serviceUUID, deviceUUID);
    
      if (deviceUUID && serviceUUID && characteristicUUID) {
          [_manager readCharacteristicForDevice:deviceUUID 
                                  serviceUUID:serviceUUID 
                           characteristicUUID:characteristicUUID];
      } else {
          NSLog(@"❌ Invalid parameters for reading characteristic");
      }
  }

  - (void)writeData:(NSData *)data 
         toDevice:(NSString *)deviceUUID 
      serviceUUID:(NSString *)serviceUUID 
characteristicUUID:(NSString *)characteristicUUID {
      NSLog(@"BluetoothBridge: Writing data to characteristic %@ on service %@ for device %@", 
            characteristicUUID, serviceUUID, deviceUUID);
    
      if (data && deviceUUID && serviceUUID && characteristicUUID) {
          [_manager writeData:data 
                   toDevice:deviceUUID 
                serviceUUID:serviceUUID 
         characteristicUUID:characteristicUUID];
      } else {
          NSLog(@"❌ Invalid parameters for writing data");
      }
  }

  #pragma mark - Enhanced Device Information Methods

//////ลบออก
  - (NSDictionary *)getDetailedDeviceInfoForUUID:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Getting detailed device info for: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          return [_manager getDetailedDeviceInfoFor:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for detailed device info");
          return @{};
      }
  }

  - (NSString *)getConnectionStateForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Getting connection state for device: %@", uuid);
    
      if (uuid && [uuid length] > 0) {

          return [_manager getConnectionState:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for connection state");
          return @"unknown";
      }
  }

  - (BOOL)isDeviceConnected:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Checking if device is connected: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          return [_manager isDeviceConnected:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for connection check");
          return NO;
      }
  }

  - (NSString *)getAvailableServicesForDevice:(NSString *)uuid {
      NSLog(@"BluetoothBridge: Getting available services for device: %@", uuid);
    
      if (uuid && [uuid length] > 0) {
          return [_manager getAvailableServicesForDevice:uuid];
      } else {
          NSLog(@"❌ Invalid UUID for services check");
          return @[];
      }
  }

  #pragma mark - Python Integration Helper Methods

  - (void)writeStringData:(NSString *)stringData 
               toDevice:(NSString *)deviceUUID 
            serviceUUID:(NSString *)serviceUUID 
     characteristicUUID:(NSString *)characteristicUUID {
      NSLog(@"BluetoothBridge: Writing string data: %@", stringData);
    
      if (stringData) {
          NSData *data = [stringData dataUsingEncoding:NSUTF8StringEncoding];
          [self writeData:data 
               toDevice:deviceUUID 
            serviceUUID:serviceUUID 
     characteristicUUID:characteristicUUID];
      } else {
          NSLog(@"❌ Invalid string data for writing");
      }
  }

  - (void)writeHexData:(NSString *)hexString 
            toDevice:(NSString *)deviceUUID 
         serviceUUID:(NSString *)serviceUUID 
  characteristicUUID:(NSString *)characteristicUUID {
      NSLog(@"BluetoothBridge: Writing hex data: %@", hexString);
    
      if (hexString) {
          NSData *data = [self dataFromHexString:hexString];
          [self writeData:data 
               toDevice:deviceUUID 
            serviceUUID:serviceUUID 
     characteristicUUID:characteristicUUID];
      } else {
          NSLog(@"❌ Invalid hex string for writing");
      }
  }

  // Helper method สำหรับแปลง hex string เป็น NSData
  - (NSData *)dataFromHexString:(NSString *)hexString {
      NSMutableData *data = [[NSMutableData alloc] init];
      unsigned char whole_byte;
      char byte_chars[3] = {'\0','\0','\0'};
    
      for (int i = 0; i < ([hexString length] / 2); i++) {
          byte_chars[0] = [hexString characterAtIndex:i*2];
          byte_chars[1] = [hexString characterAtIndex:i*2+1];
          whole_byte = strtol(byte_chars, NULL, 16);
          [data appendBytes:&whole_byte length:1];
      }
    
      return data;
  }

  #pragma mark - Enhanced Status Methods

  - (NSDictionary *)getFullSystemStatus {
      NSLog(@"BluetoothBridge: Getting full system status");
    
      NSInteger connectedCount = [self getConnectedDevicesCount];
      BOOL isScanning = [self isScanning];
      NSArray *allDevices = [self getAllDiscoveredDevices];
      NSArray *connectedDevices = [self getConnectedDevices];
    
      return @{
          @"isScanning": @(isScanning),
          @"connectedDevicesCount": @(connectedCount),
          @"totalDiscoveredDevices": @([allDevices count]),
          @"connectedDevices": connectedDevices,
          @"bluetoothState": [self getBluetoothState],
          @"timestamp": @([[NSDate date] timeIntervalSince1970])
      };
  }

  - (void)performFullDeviceScan {
      NSLog(@"BluetoothBridge: Performing full device scan with cleanup");
    
      // Clear old data
      [self clearDiscoveredDevices];
    

      // Start fresh scan ลบทิ้ง
      [self startBluetoothScan];
    
      NSLog(@"BluetoothBridge: Full device scan initiated");
  }

  #pragma mark - Error Handling and Validation

  - (BOOL)validateUUID:(NSString *)uuid {
      if (!uuid || [uuid length] == 0) {
          return NO;
      }
    
      // Basic UUID format validation
      NSString *uuidPattern = @"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$";
      NSPredicate *uuidTest = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", uuidPattern];
    
      return [uuidTest evaluateWithObject:uuid];
  }

  - (BOOL)validateServiceAndCharacteristicUUIDs:(NSString *)serviceUUID 
                           characteristicUUID:(NSString *)characteristicUUID {
      // UUIDs can be 16-bit (4 characters) or 128-bit (36 characters with dashes)
      NSString *shortUUIDPattern = @"^[0-9A-Fa-f]{4}$";
      NSString *longUUIDPattern = @"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$";
    
      NSPredicate *shortTest = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", shortUUIDPattern];
      NSPredicate *longTest = [NSPredicate predicateWithFormat:@"SELF MATCHES %@", longUUIDPattern];
    
      BOOL serviceValid = [shortTest evaluateWithObject:serviceUUID] || [longTest evaluateWithObject:serviceUUID];
      BOOL charValid = [shortTest evaluateWithObject:characteristicUUID] || [longTest evaluateWithObject:characteristicUUID];
    
      return serviceValid && charValid;
  }

  // ✅ system status
  - (void)centralManager:(CBCentralManager *)central didConnectPeripheral:(CBPeripheral *)peripheral {
      NSLog(@"✅ Connected to peripheral: %@", peripheral.name);
    
      // ✅ เพิ่มอุปกรณ์เข้า connected devices array
      if (![_connectedDevices containsObject:peripheral]) {
          [_connectedDevices addObject:peripheral];
          NSLog(@"📱 Added device to connected array. Total: %lu", (unsigned long)[_connectedDevices count]);
      }
    
      // Discover services
      [peripheral discoverServices:nil];
  }

  // ✅ system status
  - (void)centralManager:(CBCentralManager *)central didDisconnectPeripheral:(CBPeripheral *)peripheral error:(NSError *)error {
      NSLog(@"❌ Disconnected from peripheral: %@", peripheral.name);
    
      // ✅ ลบอุปกรณ์ออกจาก connected devices array
      [_connectedDevices removeObject:peripheral];
      NSLog(@"📱 Removed device from connected array. Total: %lu", (unsigned long)[_connectedDevices count]);
  }

  // เพิ่ม method สำหรับ periodic RSSI
  - (void)startPeriodicRSSIUpdatesForDevice:(NSString *)uuid withInterval:(NSTimeInterval)interval {
      NSLog(@"BluetoothBridge: Starting periodic RSSI updates for device: %@ with interval: %.1f", uuid, interval);
    
      if (uuid && [uuid length] > 0) {
          [_manager startPeriodicRSSIUpdates:uuid interval:interval];
      } else {
          NSLog(@"❌ Invalid UUID for periodic RSSI updates");
      }
  }

  - (void)stopPeriodicRSSIUpdatesForAllDevices {
      NSLog(@"BluetoothBridge: Stopping all periodic RSSI updates");
      [_manager stopPeriodicRSSIUpdates];
  }


- (void)startBeaconScan {
    [_manager startScanning];
}

- (void)stopBeaconScan {
    [_manager stopScanning];
}

#pragma mark - Beacon Region Methods

- (NSArray *)getBeaconRegions {
    NSLog(@"BluetoothBridge: Getting beacon regions");
    return [_manager getBeaconRegions];
}

- (NSString *)getBeaconRegionsAsJSON {
    NSLog(@"BluetoothBridge: Getting beacon regions as JSON");
    return [_manager getBeaconRegionsAsJSON];
}

- (NSDictionary *)getBeaconRegionByIdentifier:(NSString *)identifier {
    NSLog(@"BluetoothBridge: Getting beacon region by identifier: %@", identifier);
    if (identifier && [identifier length] > 0) {
        return [_manager getBeaconRegionByIdentifier:identifier];
    }
    return nil;
}

- (NSArray *)getAllBeaconUUIDs {
    NSLog(@"BluetoothBridge: Getting all beacon UUIDs");
    return [_manager getAllBeaconUUIDs];
}

- (NSInteger)getBeaconRegionsCount {
    NSLog(@"BluetoothBridge: Getting beacon regions count");
    return [_manager getBeaconRegionsCount];
}

- (NSDictionary *)getBeaconRegionInfo {
    NSLog(@"BluetoothBridge: Getting complete beacon region info");
    
    NSArray *regions = [self getBeaconRegions];
    NSArray *uuids = [self getAllBeaconUUIDs];
    NSInteger count = [self getBeaconRegionsCount];
    
    return @{
        @"regions": regions,
        @"uuids": uuids,
        @"count": @(count),
        @"timestamp": @([[NSDate date] timeIntervalSince1970])
    };
}

// Helper method สำหรับ Python integration
- (NSString *)getBeaconRegionInfoAsJSON {
    NSLog(@"BluetoothBridge: Getting beacon region info as JSON");
    
    NSDictionary *info = [self getBeaconRegionInfo];
    
    NSError *error;
    NSData *jsonData = [NSJSONSerialization dataWithJSONObject:info
                                                     options:NSJSONWritingPrettyPrinted
                                                       error:&error];
    if (error) {
        NSLog(@"Error converting beacon region info to JSON: %@", error.localizedDescription);
        return @"{}";
    }
    
    return [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
}
  @end
