#import "test-Bridging-Header.h"
#import "test-Swift.h"  // Replace with real name

@interface BluetoothBridge () <BluetoothScanDelegate>
@end

#import <Foundation/Foundation.h>

@interface BluetoothBridge ()
@property (nonatomic, strong) NSDictionary *lastDevice;
@end

@implementation BluetoothBridge {
    BluetoothManager *_manager;
}

- (instancetype)init {
    self = [super init];
    if (self) {
        _manager = [[BluetoothManager alloc] init];
        _manager.delegate = self;
    }
    return self;
}

- (void)startBluetoothScan {
    [_manager startScan];
}

- (void)stopBluetoothScan {
    [_manager stopScan];
}

- (void)didDiscoverDeviceWithName:(NSString *)name
                             uuid:(NSString *)uuid
                             rssi:(NSInteger)rssi
                            major:(NSInteger)major
                            minor:(NSInteger)minor {
    
    NSDictionary *userInfo = @{
        @"name": name ?: @"Unknown",
        @"uuid": uuid,
        @"rssi": @(rssi),
        @"major": @(major),
        @"minor": @(minor)
    };

    [[NSNotificationCenter defaultCenter] postNotificationName:@"BluetoothDeviceDiscovered"
                                                        object:nil
                                                      userInfo:userInfo];
    self.lastDevice = @{
        @"name": name ?: @"Unknown",
        @"uuid": uuid ?: @"",
        @"rssi": @(rssi),
        @"major": @(major),
        @"minor": @(minor)
    };

    // ✅ You can store it or send it to Python

}

- (void)connectToDeviceWithUUID:(NSString *)uuid {
    [_manager connectToPeripheralWith:uuid];
}

- (NSDictionary *)getLastDiscoveredDevice {
    return self.lastDevice;
}

@end
