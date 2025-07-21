#!/usr/bin/env python3
"""
Hikvision CCTV Camera Access Script

This script demonstrates how to access and view video streams from Hikvision cameras
using OpenCV and the RTSP protocol.
"""

import cv2
import argparse
import time
import os
from datetime import datetime

def access_hikvision_camera(ip, username, password, port=554, channel=1, subtype=0, output_dir=None):
    """
    Access a Hikvision camera stream using RTSP protocol.
    
    Args:
        ip (str): IP address of the camera
        username (str): Username for authentication
        password (str): Password for authentication
        port (int): RTSP port (default: 554)
        channel (int): Camera channel (default: 1)
        subtype (int): Stream type - 0 for main stream, 1 for sub stream (default: 0)
        output_dir (str): Directory to save captured images (default: None)
    
    Returns:
        None
    """
    # Construct the RTSP URL
    rtsp_url = f"rtsp://{username}:{password}@{ip}:{port}/Streaming/Channels/{channel}{subtype}"
    print(f"Connecting to: {rtsp_url.replace(password, '********')}")
    
    # Create output directory if specified
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Open the RTSP stream
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("Error: Could not connect to the camera.")
        return
    
    print("Successfully connected to the camera.")
    print("Press 'q' to quit, 's' to save a snapshot")
    
    try:
        while True:
            # Read a frame from the stream
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Failed to receive frame from stream.")
                break
            
            # Display the frame
            cv2.imshow('Hikvision Camera Stream', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            # Press 'q' to quit
            if key == ord('q'):
                break
                
            # Press 's' to save a snapshot
            elif key == ord('s') and output_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(output_dir, f"hikvision_snapshot_{timestamp}.jpg")
                cv2.imwrite(filename, frame)
                print(f"Snapshot saved: {filename}")
                
    except KeyboardInterrupt:
        print("Stream interrupted by user.")
    finally:
        # Release resources
        cap.release()
        cv2.destroyAllWindows()
        print("Connection closed.")

def access_hikvision_isapi(ip, username, password, port=80):
    """
    Access Hikvision camera using the ISAPI interface.
    This is a placeholder for ISAPI functionality.
    
    Args:
        ip (str): IP address of the camera
        username (str): Username for authentication
        password (str): Password for authentication
        port (int): HTTP port (default: 80)
    
    Returns:
        None
    """
    print("ISAPI access is not implemented in this basic example.")
    print("ISAPI would allow you to control PTZ, access configuration, and more.")
    print(f"You would typically access the ISAPI at: http://{ip}:{port}/ISAPI/")

def main():
    """Main function to parse arguments and call appropriate functions."""
    parser = argparse.ArgumentParser(description='Access Hikvision CCTV Camera')
    parser.add_argument('--ip', required=True, help='IP address of the camera')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--password', required=True, help='Password for authentication')
    parser.add_argument('--port', type=int, default=554, help='RTSP port (default: 554)')
    parser.add_argument('--channel', type=int, default=1, help='Camera channel (default: 1)')
    parser.add_argument('--subtype', type=int, default=0, 
                        help='Stream type - 0 for main stream, 1 for sub stream (default: 0)')
    parser.add_argument('--output', help='Directory to save captured images')
    parser.add_argument('--isapi', action='store_true', help='Use ISAPI interface instead of RTSP')
    
    args = parser.parse_args()
    
    if args.isapi:
        access_hikvision_isapi(args.ip, args.username, args.password, port=80)
    else:
        access_hikvision_camera(
            args.ip, 
            args.username, 
            args.password, 
            args.port, 
            args.channel, 
            args.subtype,
            args.output
        )

if __name__ == "__main__":
    main()