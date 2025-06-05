#import <Foundation/Foundation.h>

@interface BluetoothBridge : NSObject

- (void)startBluetoothScan;
- (void)stopBluetoothScan;

// This method will be called from Swift with scan results
- (void)didDiscoverDeviceWithName:(NSString *)name
                             uuid:(NSString *)uuid
                             rssi:(NSInteger)rssi
                            major:(NSInteger)major
                            minor:(NSInteger)minor;

- (void)connectToDeviceWithUUID:(NSString *)uuid;
- (NSDictionary *)getLastDiscoveredDevice;

@end
