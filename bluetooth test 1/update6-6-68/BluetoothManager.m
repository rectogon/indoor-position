  #import "test-Bridging-Header.h"
  #import "test-Swift.h"  // Replace with your actual Swift header name

  @interface BluetoothBridge () <BluetoothScanDelegate>
  @property (nonatomic, strong) BluetoothManager *manager;
  @property (nonatomic, strong) NSDictionary *lastDevice;
  @property (nonatomic, strong) NSMutableArray *discoveredDevices;
  @property (nonatomic, strong) NSMutableArray *connectedDevices;
  @property (nonatomic, assign) BOOL isCurrentlyScanning;
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
      NSInteger count = [_manager getConnectedPeripheralsCount];
      NSLog(@"BluetoothBridge: getConnectedDevicesCount called, returning: %ld", (long)count);
      return count;
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

  @end
