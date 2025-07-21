# Hikvision CCTV Camera Access with Python

This repository contains Python scripts for accessing and controlling Hikvision CCTV cameras. These scripts demonstrate various methods to interact with Hikvision cameras, from basic video streaming to advanced PTZ control and motion detection.

## Prerequisites

Before using these scripts, you'll need:

1. Python 3.6 or higher
2. OpenCV library (`pip install opencv-python`)
3. Requests library (`pip install requests`)
4. A Hikvision camera with network connectivity
5. Camera access credentials (IP address, username, password)

## Installation

```bash
# Install required dependencies
pip install opencv-python numpy requests
```

## Scripts Overview

### 1. Basic Camera Access (`hikvision_access.py`)

This script demonstrates basic RTSP streaming from a Hikvision camera.

**Features:**
- Connect to camera via RTSP
- View live video stream
- Capture snapshots

**Usage:**
```bash
python hikvision_access.py --ip 192.168.1.100 --username admin --password your_password --output ./snapshots
```

### 2. Advanced Camera Control (`hikvision_advanced.py`)

This script provides more advanced functionality including PTZ control, motion detection, and recording.

**Features:**
- Connect to camera via RTSP
- View live video stream
- Record video
- Capture snapshots
- Basic motion detection
- PTZ control via ISAPI
- Device information retrieval

**Usage:**
```bash
python hikvision_advanced.py --ip 192.168.1.100 --username admin --password your_password --output ./output
```

**Interactive Controls:**
- `q` - Quit
- `s` - Save snapshot
- `r` - Start/stop recording
- `m` - Motion detection
- `i` - Device information
- Arrow keys - Pan/Tilt (if PTZ supported)
- `+`/`-` - Zoom in/out (if PTZ supported)

### 3. SDK Example (`hikvision_sdk_example.py`)

This script demonstrates how to use the Hikvision SDK (if available) for more advanced control.

**Note:** This script requires the Hikvision SDK, which is typically available from Hikvision directly. The script is provided as a template and may need adjustments based on the specific SDK version.

**Features:**
- Connect using the native SDK
- Capture high-quality snapshots
- PTZ control
- Device information retrieval
- Recording control

**Usage:**
```bash
python hikvision_sdk_example.py --ip 192.168.1.100 --username admin --password your_password --output ./output --capture
```

## Connection Methods

These scripts demonstrate three main methods to connect to Hikvision cameras:

1. **RTSP Protocol** - Used for video streaming
   - URL format: `rtsp://username:password@ip:port/Streaming/Channels/channel_number`
   - Default port: 554

2. **ISAPI HTTP Interface** - Used for camera control and configuration
   - URL format: `http://ip:port/ISAPI/...`
   - Default port: 80

3. **Hikvision SDK** - Used for advanced control (requires SDK installation)
   - Provides the most comprehensive access to camera features
   - Typically requires registration with Hikvision to obtain

## Common Issues and Troubleshooting

### Connection Issues
- Ensure the camera is accessible on the network (try pinging it)
- Verify username and password are correct
- Check if the camera's RTSP service is enabled
- Some cameras require specific URL formats - check your camera's documentation

### Video Streaming Issues
- Try different channel numbers (typically 1, 101, or 102)
- Try both main stream (0) and sub stream (1)
- Some cameras have bandwidth limitations for multiple connections

### PTZ Control Issues
- Ensure the camera supports PTZ functionality
- Verify user has PTZ control permissions
- Some cameras require specific protocols for PTZ control

## Security Considerations

- Always use strong passwords for your cameras
- Consider using a dedicated VLAN for security cameras
- Avoid exposing camera interfaces directly to the internet
- Update camera firmware regularly

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- These scripts are provided for educational purposes
- Hikvision® is a registered trademark of Hangzhou Hikvision Digital Technology Co., Ltd.
- This project is not affiliated with or endorsed by Hikvision