//
//  Use this file to import your target's public headers that you would like to expose to Swift.
//

#import <Foundation/Foundation.h>

@interface BluetoothBridge : NSObject

// Basic scanning methods
- (void)startBluetoothScan;
- (void)stopBluetoothScan;

// Device discovery callback
- (void)didDiscoverDeviceWithName:(NSString *)name
                             uuid:(NSString *)uuid
                             rssi:(NSInteger)rssi
                            major:(NSInteger)major
                            minor:(NSInteger)minor;

// Connection methods
- (void)connectToDeviceWithUUID:(NSString *)uuid;
- (void)disconnectFromDeviceWithUUID:(NSString *)uuid;
- (void)reconnectToDeviceWithUUID:(NSString *)uuid;

// Connection status callbacks
- (void)didConnectToDeviceWithUUID:(NSString *)uuid;
- (void)didDisconnectFromDeviceWithUUID:(NSString *)uuid error:(NSString *)errorMessage;
- (void)didFailToConnectToDeviceWithUUID:(NSString *)uuid error:(NSString *)errorMessage;

// Configuration methods
- (void)setAutoReconnectEnabled:(BOOL)enabled;
- (void)setMaxReconnectAttempts:(NSInteger)attempts;

// Data retrieval methods
- (NSDictionary *)getLastDiscoveredDevice;
- (NSArray *)getAllDiscoveredDevices;
- (NSArray *)getConnectedDevices;
- (NSInteger)getConnectedDevicesCount;

// Status methods
- (BOOL)isScanning;
- (BOOL)isBluetoothEnabled;
- (NSString *)getBluetoothState;

@end
