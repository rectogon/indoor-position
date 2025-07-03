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

// เพิ่ม RSSI methods
- (void)startRSSIUpdatesForDevice:(NSString *)uuid;
- (void)stopRSSIUpdatesForDevice:(NSString *)uuid;
- (NSInteger)getCurrentRSSIForDevice:(NSString *)uuid;

// เพิ่ม methods ใหม่
- (void)clearDiscoveredDevices;
- (BOOL)hasDiscoveredDevices;
- (NSDictionary *)getLastDiscoveredDeviceForced;

// เพิ่ม method declarations เหล่านี้
- (NSString *)getConnectionState:(NSString *)uuid;
- (BOOL)isDeviceConnected:(NSString *)uuid;
- (NSArray *)getAvailableServices:(NSString *)uuid;
- (void)startConnectionForDevice:(NSString *)uuid;

// เพิ่ม methods สำหรับ detailed device info
- (NSDictionary *)getDetailedDeviceInfo:(NSString *)uuid;
- (NSDictionary *)getCurrentBatteryInfo;
- (NSInteger)getBatteryLevelForDevice:(NSString *)uuid;
- (void)requestBatteryUpdateForDevice:(NSString *)uuid;


- (void)startBeaconScan;
- (void)stopBeaconScan;

@end
