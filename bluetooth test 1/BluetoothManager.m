#import "test-Bridging-Header.h"
#import "test-Swift.h"  // Replace with your actual Swift header name

@interface BluetoothBridge () <BluetoothScanDelegate>
@property (nonatomic, strong) BluetoothManager *manager;
@property (nonatomic, strong) NSDictionary *lastDevice;
@end

@implementation BluetoothBridge

- (instancetype)init {
    self = [super init];
    if (self) {
        _manager = [[BluetoothManager alloc] init];
        _manager.delegate = self;
        NSLog(@"BluetoothBridge initialized with manager: %@", _manager);
    }
    return self;
}

- (void)startBluetoothScan {
    NSLog(@"BluetoothBridge: Starting scan...");
    [_manager startScan];
}

- (void)stopBluetoothScan {
    NSLog(@"BluetoothBridge: Stopping scan...");
    [_manager stopScan];
}

// This method will be called by Swift BluetoothManager
- (void)didDiscoverDeviceWithName:(NSString *)name
                             uuid:(NSString *)uuid
                             rssi:(NSInteger)rssi
                            major:(NSInteger)major
                            minor:(NSInteger)minor {
    
    NSLog(@"BluetoothBridge: Device discovered - Name: %@, UUID: %@, RSSI: %ld", 
          name, uuid, (long)rssi);
    
    self.lastDevice = @{
        @"name": name ?: @"Unknown",
        @"uuid": uuid ?: @"",
        @"rssi": @(rssi),
        @"major": @(major),
        @"minor": @(minor)
    };
    
    NSLog(@"BluetoothBridge: lastDevice set to: %@", self.lastDevice);
}

- (void)connectToDeviceWithUUID:(NSString *)uuid {
    [_manager connectToPeripheralWith:uuid];
}

- (NSDictionary *)getLastDiscoveredDevice {
    NSLog(@"BluetoothBridge: getLastDiscoveredDevice called, returning: %@", self.lastDevice);
    return self.lastDevice;
}

@end
