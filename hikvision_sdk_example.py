#!/usr/bin/env python3
"""
Hikvision SDK Example

This script demonstrates how to use the Hikvision SDK (if available) for advanced camera control.
Note: This requires the Hikvision SDK to be installed, which is typically available from Hikvision.

Important: This is a template/example script. The actual SDK implementation may vary depending on
the specific SDK version and available bindings.
"""

import os
import sys
import time
from datetime import datetime
import argparse

# Try to import the Hikvision SDK
try:
    # The actual import might be different depending on how the SDK is installed
    # This is just an example based on common SDK patterns
    import HCNetSDK
    HAS_SDK = True
except ImportError:
    print("Warning: Hikvision SDK (HCNetSDK) not found.")
    print("This script requires the Hikvision SDK to be installed.")
    print("You can obtain it from Hikvision or use the RTSP/ISAPI methods instead.")
    HAS_SDK = False

class HikvisionSDKCamera:
    """Class to handle Hikvision camera operations using the SDK."""
    
    def __init__(self, ip, username, password, port=8000, output_dir=None):
        """
        Initialize the Hikvision camera connection using SDK.
        
        Args:
            ip (str): IP address of the camera
            username (str): Username for authentication
            password (str): Password for authentication
            port (int): Device port (default: 8000)
            output_dir (str): Directory to save captured images and videos (default: None)
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.output_dir = output_dir
        self.user_id = -1
        self.sdk_initialized = False
        
        # Create output directory if specified
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
        
        # Initialize SDK if available
        if HAS_SDK:
            self.sdk_initialized = self._initialize_sdk()
        else:
            print("SDK not available. Functionality will be limited.")
    
    def _initialize_sdk(self):
        """Initialize the Hikvision SDK."""
        try:
            # Initialize the SDK
            init_result = HCNetSDK.NET_DVR_Init()
            if not init_result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Failed to initialize SDK. Error code: {error_code}")
                return False
            
            # Set connection timeout
            HCNetSDK.NET_DVR_SetConnectTime(2000, 1)
            HCNetSDK.NET_DVR_SetReconnect(10000, True)
            
            print("SDK initialized successfully.")
            return True
            
        except Exception as e:
            print(f"Error initializing SDK: {e}")
            return False
    
    def connect(self):
        """Connect to the camera using the SDK."""
        if not HAS_SDK or not self.sdk_initialized:
            print("SDK not available or not initialized.")
            return False
        
        try:
            # Create login parameters
            login_info = HCNetSDK.NET_DVR_USER_LOGIN_INFO()
            device_info = HCNetSDK.NET_DVR_DEVICEINFO_V40()
            
            # Set login parameters
            login_info.sDeviceAddress = self.ip.encode('utf-8')
            login_info.wPort = self.port
            login_info.sUserName = self.username.encode('utf-8')
            login_info.sPassword = self.password.encode('utf-8')
            
            # Login to the device
            self.user_id = HCNetSDK.NET_DVR_Login_V40(login_info, device_info)
            
            if self.user_id < 0:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Login failed. Error code: {error_code}")
                return False
            
            print(f"Login successful. User ID: {self.user_id}")
            return True
            
        except Exception as e:
            print(f"Error connecting to camera: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the camera."""
        if not HAS_SDK or not self.sdk_initialized:
            return
        
        if self.user_id >= 0:
            # Logout from the device
            logout_result = HCNetSDK.NET_DVR_Logout(self.user_id)
            if not logout_result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Logout failed. Error code: {error_code}")
            else:
                print("Logout successful.")
                self.user_id = -1
    
    def cleanup(self):
        """Clean up SDK resources."""
        if not HAS_SDK or not self.sdk_initialized:
            return
        
        # Ensure we're logged out
        if self.user_id >= 0:
            self.disconnect()
        
        # Clean up SDK resources
        cleanup_result = HCNetSDK.NET_DVR_Cleanup()
        if not cleanup_result:
            error_code = HCNetSDK.NET_DVR_GetLastError()
            print(f"SDK cleanup failed. Error code: {error_code}")
        else:
            print("SDK resources cleaned up.")
            self.sdk_initialized = False
    
    def capture_picture(self):
        """Capture a picture using the SDK."""
        if not HAS_SDK or not self.sdk_initialized or self.user_id < 0:
            print("Cannot capture picture. Not connected to camera.")
            return False
        
        if not self.output_dir:
            print("Error: No output directory specified.")
            return False
        
        try:
            # Create picture parameters
            pic_param = HCNetSDK.NET_DVR_JPEGPARA()
            pic_param.wPicQuality = 0  # Best quality
            pic_param.wPicSize = 0xFF  # Use current stream resolution
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"hikvision_sdk_snapshot_{timestamp}.jpg")
            
            # Capture picture
            result = HCNetSDK.NET_DVR_CaptureJPEGPicture(
                self.user_id, 1, pic_param, filename.encode('utf-8')
            )
            
            if not result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Picture capture failed. Error code: {error_code}")
                return False
            
            print(f"Picture captured successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error capturing picture: {e}")
            return False
    
    def ptz_control(self, command, speed=4, stop=True):
        """
        Control PTZ functions using the SDK.
        
        Args:
            command (str): PTZ command ('left', 'right', 'up', 'down', 'zoom_in', 'zoom_out')
            speed (int): Movement speed (1-7)
            stop (bool): Whether to automatically stop the movement after a short delay
        
        Returns:
            bool: True if command was successful, False otherwise
        """
        if not HAS_SDK or not self.sdk_initialized or self.user_id < 0:
            print("Cannot control PTZ. Not connected to camera.")
            return False
        
        # Map commands to SDK command codes
        ptz_commands = {
            'left': HCNetSDK.TILT_LEFT,
            'right': HCNetSDK.TILT_RIGHT,
            'up': HCNetSDK.TILT_UP,
            'down': HCNetSDK.TILT_DOWN,
            'zoom_in': HCNetSDK.ZOOM_IN,
            'zoom_out': HCNetSDK.ZOOM_OUT
        }
        
        if command not in ptz_commands:
            print(f"Error: Unknown PTZ command '{command}'")
            return False
        
        # Validate speed
        speed = max(1, min(7, speed))
        
        try:
            # Start PTZ movement
            result = HCNetSDK.NET_DVR_PTZControlWithSpeed(
                self.user_id, 1, ptz_commands[command], 0, speed
            )
            
            if not result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"PTZ control failed. Error code: {error_code}")
                return False
            
            print(f"PTZ command '{command}' sent successfully")
            
            # Stop movement after a short delay if requested
            if stop:
                time.sleep(0.5)  # Move for half a second
                stop_result = HCNetSDK.NET_DVR_PTZControlWithSpeed(
                    self.user_id, 1, ptz_commands[command], 1, speed
                )
                
                if not stop_result:
                    error_code = HCNetSDK.NET_DVR_GetLastError()
                    print(f"PTZ stop failed. Error code: {error_code}")
            
            return True
            
        except Exception as e:
            print(f"Error controlling PTZ: {e}")
            return False
    
    def get_device_info(self):
        """
        Get device information using the SDK.
        
        Returns:
            dict: Device information or None if failed
        """
        if not HAS_SDK or not self.sdk_initialized or self.user_id < 0:
            print("Cannot get device info. Not connected to camera.")
            return None
        
        try:
            # Create device info structure
            device_info = HCNetSDK.NET_DVR_DEVICECFG()
            
            # Get device info
            result = HCNetSDK.NET_DVR_GetDVRConfig(
                self.user_id, HCNetSDK.NET_DVR_GET_DEVICECFG,
                0, device_info, HCNetSDK.SERIALNO_LEN
            )
            
            if not result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Get device info failed. Error code: {error_code}")
                return None
            
            # Extract device information
            info = {
                'deviceName': device_info.sDVRName.decode('utf-8').strip('\0'),
                'serialNumber': device_info.sSerialNumber.decode('utf-8').strip('\0'),
                'deviceType': device_info.wDVRType,
                'channelCount': device_info.byChanNum,
                'diskCount': device_info.byDiskNum
            }
            
            print("Device Information:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
            return info
            
        except Exception as e:
            print(f"Error getting device info: {e}")
            return None
    
    def start_record(self, channel=1):
        """
        Start recording from a channel using the SDK.
        
        Args:
            channel (int): Channel number to record from
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_SDK or not self.sdk_initialized or self.user_id < 0:
            print("Cannot start recording. Not connected to camera.")
            return False
        
        if not self.output_dir:
            print("Error: No output directory specified.")
            return False
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"hikvision_sdk_recording_{timestamp}.mp4")
            
            # Start recording
            result = HCNetSDK.NET_DVR_StartDVRRecord(self.user_id, channel, 0)
            
            if not result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Start recording failed. Error code: {error_code}")
                return False
            
            print(f"Recording started on channel {channel}")
            return True
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False
    
    def stop_record(self, channel=1):
        """
        Stop recording from a channel using the SDK.
        
        Args:
            channel (int): Channel number to stop recording from
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not HAS_SDK or not self.sdk_initialized or self.user_id < 0:
            print("Cannot stop recording. Not connected to camera.")
            return False
        
        try:
            # Stop recording
            result = HCNetSDK.NET_DVR_StopDVRRecord(self.user_id, channel)
            
            if not result:
                error_code = HCNetSDK.NET_DVR_GetLastError()
                print(f"Stop recording failed. Error code: {error_code}")
                return False
            
            print(f"Recording stopped on channel {channel}")
            return True
            
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False

def main():
    """Main function to parse arguments and initialize camera."""
    parser = argparse.ArgumentParser(description='Hikvision SDK Example')
    parser.add_argument('--ip', required=True, help='IP address of the camera')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--password', required=True, help='Password for authentication')
    parser.add_argument('--port', type=int, default=8000, help='Device port (default: 8000)')
    parser.add_argument('--output', default='./output', help='Directory to save captured images and videos')
    parser.add_argument('--capture', action='store_true', help='Capture a picture')
    parser.add_argument('--info', action='store_true', help='Get device information')
    parser.add_argument('--ptz', choices=['left', 'right', 'up', 'down', 'zoom_in', 'zoom_out'],
                        help='Send PTZ command')
    parser.add_argument('--speed', type=int, default=4, help='PTZ speed (1-7, default: 4)')
    
    args = parser.parse_args()
    
    # Check if SDK is available
    if not HAS_SDK:
        print("Error: Hikvision SDK not available. Cannot proceed.")
        return
    
    # Create camera object
    camera = HikvisionSDKCamera(
        args.ip,
        args.username,
        args.password,
        args.port,
        args.output
    )
    
    try:
        # Connect to the camera
        if not camera.connect():
            print("Failed to connect to camera. Exiting.")
            return
        
        # Handle different operations
        if args.capture:
            camera.capture_picture()
        elif args.info:
            camera.get_device_info()
        elif args.ptz:
            camera.ptz_control(args.ptz, args.speed)
        else:
            # Default: just get device info
            camera.get_device_info()
        
    finally:
        # Clean up
        camera.disconnect()
        camera.cleanup()

if __name__ == "__main__":
    main()