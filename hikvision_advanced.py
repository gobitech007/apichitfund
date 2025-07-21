#!/usr/bin/env python3
"""
Advanced Hikvision CCTV Camera Access Script

This script demonstrates advanced functionality for Hikvision cameras including:
- Video streaming via RTSP
- Recording video
- PTZ control via ISAPI
- Motion detection
- System information retrieval
"""

import cv2
import numpy as np
import argparse
import time
import os
import requests
from datetime import datetime
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import threading

class HikvisionCamera:
    """Class to handle Hikvision camera operations."""
    
    def __init__(self, ip, username, password, rtsp_port=554, http_port=80, 
                 channel=1, subtype=0, output_dir=None):
        """
        Initialize the Hikvision camera connection.
        
        Args:
            ip (str): IP address of the camera
            username (str): Username for authentication
            password (str): Password for authentication
            rtsp_port (int): RTSP port (default: 554)
            http_port (int): HTTP port for ISAPI (default: 80)
            channel (int): Camera channel (default: 1)
            subtype (int): Stream type - 0 for main stream, 1 for sub stream (default: 0)
            output_dir (str): Directory to save captured images and videos (default: None)
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.rtsp_port = rtsp_port
        self.http_port = http_port
        self.channel = channel
        self.subtype = subtype
        self.output_dir = output_dir
        self.rtsp_url = f"rtsp://{username}:{password}@{ip}:{rtsp_port}/Streaming/Channels/{channel}{subtype}"
        self.isapi_base_url = f"http://{ip}:{http_port}/ISAPI"
        self.cap = None
        self.is_recording = False
        self.recording_thread = None
        self.stop_recording = False
        
        # Create output directory if specified
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")
    
    def connect(self):
        """Connect to the camera's RTSP stream."""
        print(f"Connecting to: {self.rtsp_url.replace(self.password, '********')}")
        
        self.cap = cv2.VideoCapture(self.rtsp_url)
        
        if not self.cap.isOpened():
            print("Error: Could not connect to the camera.")
            return False
        
        print("Successfully connected to the camera.")
        return True
    
    def disconnect(self):
        """Disconnect from the camera stream."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            print("Disconnected from camera stream.")
    
    def get_frame(self):
        """Get a single frame from the camera."""
        if not self.cap or not self.cap.isOpened():
            print("Error: Camera connection not established.")
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to receive frame from stream.")
            return None
        
        return frame
    
    def save_snapshot(self, frame=None):
        """Save a snapshot from the camera."""
        if not self.output_dir:
            print("Error: No output directory specified.")
            return
        
        if frame is None:
            frame = self.get_frame()
            
        if frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"hikvision_snapshot_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            print(f"Snapshot saved: {filename}")
    
    def start_recording(self, duration=None):
        """
        Start recording video from the camera.
        
        Args:
            duration (int): Recording duration in seconds (None for indefinite)
        """
        if self.is_recording:
            print("Already recording.")
            return
        
        if not self.output_dir:
            print("Error: No output directory specified.")
            return
        
        self.is_recording = True
        self.stop_recording = False
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(
            target=self._record_video_thread,
            args=(duration,)
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop the current recording."""
        if not self.is_recording:
            print("Not currently recording.")
            return
        
        self.stop_recording = True
        if self.recording_thread:
            self.recording_thread.join()
        
        print("Recording stopped.")
    
    def _record_video_thread(self, duration=None):
        """
        Thread function to handle video recording.
        
        Args:
            duration (int): Recording duration in seconds (None for indefinite)
        """
        if not self.cap or not self.cap.isOpened():
            print("Error: Camera connection not established.")
            self.is_recording = False
            return
        
        # Get video properties
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"hikvision_recording_{timestamp}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
        
        print(f"Started recording to: {filename}")
        start_time = time.time()
        
        try:
            while self.cap.isOpened() and not self.stop_recording:
                # Check if duration has elapsed
                if duration and (time.time() - start_time) > duration:
                    break
                
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to receive frame during recording.")
                    break
                
                # Write frame to video file
                out.write(frame)
                
                # Small delay to prevent maxing out CPU
                time.sleep(0.001)
        
        finally:
            out.release()
            print(f"Recording saved: {filename}")
            self.is_recording = False
    
    def detect_motion(self, sensitivity=20, display=True, duration=30):
        """
        Perform basic motion detection.
        
        Args:
            sensitivity (int): Motion detection sensitivity (1-100)
            display (bool): Whether to display the video with motion indicators
            duration (int): How long to run motion detection for (seconds)
        
        Returns:
            bool: True if motion was detected, False otherwise
        """
        if not self.cap or not self.cap.isOpened():
            print("Error: Camera connection not established.")
            return False
        
        print(f"Starting motion detection (sensitivity: {sensitivity})")
        
        # Convert sensitivity to threshold (inverse relationship)
        threshold = int(255 * (100 - sensitivity) / 100)
        
        # Get first frame for comparison
        ret, prev_frame = self.cap.read()
        if not ret:
            print("Error: Failed to receive initial frame for motion detection.")
            return False
        
        # Convert to grayscale and blur for noise reduction
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
        
        motion_detected = False
        start_time = time.time()
        
        try:
            while self.cap.isOpened():
                # Check if duration has elapsed
                if duration and (time.time() - start_time) > duration:
                    break
                
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to receive frame during motion detection.")
                    break
                
                # Process frame for motion detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                
                # Compute absolute difference between current and previous frame
                frame_delta = cv2.absdiff(prev_gray, gray)
                thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
                
                # Dilate the thresholded image to fill in holes
                thresh = cv2.dilate(thresh, None, iterations=2)
                
                # Find contours on thresholded image
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Check for significant motion
                significant_motion = False
                for contour in contours:
                    if cv2.contourArea(contour) < 500:  # Ignore small contours
                        continue
                    
                    significant_motion = True
                    motion_detected = True
                    
                    if display:
                        (x, y, w, h) = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Display the resulting frame if requested
                if display:
                    # Add motion status text
                    status_text = "Motion Detected" if significant_motion else "No Motion"
                    color = (0, 0, 255) if significant_motion else (0, 255, 0)
                    cv2.putText(frame, f"Status: {status_text}", (10, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    cv2.imshow("Motion Detection", frame)
                    
                    # Break on 'q' key press
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Update previous frame
                prev_gray = gray
                
                # Small delay to prevent maxing out CPU
                time.sleep(0.01)
        
        finally:
            if display:
                cv2.destroyWindow("Motion Detection")
            
            print(f"Motion detection ended. Motion detected: {motion_detected}")
            return motion_detected
    
    def ptz_control(self, command, speed=5):
        """
        Control PTZ (Pan-Tilt-Zoom) functions via ISAPI.
        
        Args:
            command (str): PTZ command ('left', 'right', 'up', 'down', 'zoom_in', 'zoom_out', 'stop')
            speed (int): Movement speed (1-10)
        
        Returns:
            bool: True if command was successful, False otherwise
        """
        # Validate speed
        speed = max(1, min(10, speed))
        
        # Map commands to PTZ parameters
        ptz_commands = {
            'left': {'pan': -speed, 'tilt': 0, 'zoom': 0},
            'right': {'pan': speed, 'tilt': 0, 'zoom': 0},
            'up': {'pan': 0, 'tilt': speed, 'zoom': 0},
            'down': {'pan': 0, 'tilt': -speed, 'zoom': 0},
            'zoom_in': {'pan': 0, 'tilt': 0, 'zoom': speed},
            'zoom_out': {'pan': 0, 'tilt': 0, 'zoom': -speed},
            'stop': {'pan': 0, 'tilt': 0, 'zoom': 0}
        }
        
        if command not in ptz_commands:
            print(f"Error: Unknown PTZ command '{command}'")
            return False
        
        # Get PTZ parameters for the command
        params = ptz_commands[command]
        
        # Create XML for PTZ request
        xml_data = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <PTZData>
            <pan>{params['pan']}</pan>
            <tilt>{params['tilt']}</tilt>
            <zoom>{params['zoom']}</zoom>
        </PTZData>
        """
        
        # Send PTZ command
        url = f"{self.isapi_base_url}/PTZCtrl/channels/{self.channel}/continuous"
        try:
            response = requests.put(
                url,
                auth=HTTPDigestAuth(self.username, self.password),
                data=xml_data,
                headers={'Content-Type': 'application/xml'},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"PTZ command '{command}' sent successfully")
                return True
            else:
                print(f"Error sending PTZ command: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error sending PTZ command: {e}")
            return False
    
    def get_device_info(self):
        """
        Get device information via ISAPI.
        
        Returns:
            dict: Device information or None if failed
        """
        url = f"{self.isapi_base_url}/System/deviceInfo"
        try:
            response = requests.get(
                url,
                auth=HTTPDigestAuth(self.username, self.password),
                timeout=5
            )
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.text)
                
                # Extract device information
                device_info = {
                    'deviceName': root.find('deviceName').text if root.find('deviceName') is not None else 'Unknown',
                    'deviceID': root.find('deviceID').text if root.find('deviceID') is not None else 'Unknown',
                    'model': root.find('model').text if root.find('model') is not None else 'Unknown',
                    'serialNumber': root.find('serialNumber').text if root.find('serialNumber') is not None else 'Unknown',
                    'firmwareVersion': root.find('firmwareVersion').text if root.find('firmwareVersion') is not None else 'Unknown',
                    'firmwareReleasedDate': root.find('firmwareReleasedDate').text if root.find('firmwareReleasedDate') is not None else 'Unknown',
                }
                
                print("Device Information:")
                for key, value in device_info.items():
                    print(f"  {key}: {value}")
                
                return device_info
            else:
                print(f"Error getting device information: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting device information: {e}")
            return None
    
    def stream_video(self):
        """Stream video from the camera and provide interactive controls."""
        if not self.connect():
            return
        
        print("\nControls:")
        print("  q - Quit")
        print("  s - Save snapshot")
        print("  r - Start/stop recording")
        print("  m - Motion detection")
        print("  i - Device information")
        print("PTZ Controls (if supported):")
        print("  Arrow keys - Pan/Tilt")
        print("  +/- - Zoom in/out")
        
        recording = False
        
        try:
            while True:
                frame = self.get_frame()
                if frame is None:
                    break
                
                # Add recording indicator if recording
                if recording:
                    cv2.putText(frame, "REC", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0, 0, 255), 2)
                
                # Display the frame
                cv2.imshow('Hikvision Camera Stream', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):  # Quit
                    break
                elif key == ord('s'):  # Save snapshot
                    self.save_snapshot(frame)
                elif key == ord('r'):  # Toggle recording
                    if recording:
                        self.stop_recording = True
                        recording = False
                        print("Recording stopped")
                    else:
                        self.start_recording()
                        recording = True
                        print("Recording started")
                elif key == ord('m'):  # Motion detection
                    cv2.destroyAllWindows()
                    self.detect_motion()
                    # Reconnect after motion detection
                    self.disconnect()
                    self.connect()
                elif key == ord('i'):  # Device information
                    self.get_device_info()
                # PTZ controls
                elif key == 81:  # Left arrow
                    self.ptz_control('left')
                elif key == 83:  # Right arrow
                    self.ptz_control('right')
                elif key == 82:  # Up arrow
                    self.ptz_control('up')
                elif key == 84:  # Down arrow
                    self.ptz_control('down')
                elif key == ord('+'):  # Zoom in
                    self.ptz_control('zoom_in')
                elif key == ord('-'):  # Zoom out
                    self.ptz_control('zoom_out')
                
        except KeyboardInterrupt:
            print("Stream interrupted by user.")
        finally:
            # Clean up
            if recording:
                self.stop_recording = True
            self.disconnect()
            cv2.destroyAllWindows()

def main():
    """Main function to parse arguments and initialize camera."""
    parser = argparse.ArgumentParser(description='Advanced Hikvision CCTV Camera Access')
    parser.add_argument('--ip', required=True, help='IP address of the camera')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--password', required=True, help='Password for authentication')
    parser.add_argument('--rtsp-port', type=int, default=554, help='RTSP port (default: 554)')
    parser.add_argument('--http-port', type=int, default=80, help='HTTP port for ISAPI (default: 80)')
    parser.add_argument('--channel', type=int, default=1, help='Camera channel (default: 1)')
    parser.add_argument('--subtype', type=int, default=0, 
                        help='Stream type - 0 for main stream, 1 for sub stream (default: 0)')
    parser.add_argument('--output', default='./output', help='Directory to save captured images and videos')
    parser.add_argument('--info', action='store_true', help='Get device information only')
    parser.add_argument('--motion', action='store_true', help='Run motion detection only')
    
    args = parser.parse_args()
    
    # Create camera object
    camera = HikvisionCamera(
        args.ip,
        args.username,
        args.password,
        args.rtsp_port,
        args.http_port,
        args.channel,
        args.subtype,
        args.output
    )
    
    # Handle different modes
    if args.info:
        camera.get_device_info()
    elif args.motion:
        camera.connect()
        camera.detect_motion()
        camera.disconnect()
    else:
        camera.stream_video()

if __name__ == "__main__":
    main()