#!/usr/bin/env python3
# encoding: utf-8
"""
Camera Test Script for TonyPi Robot

This script tests the camera functionality and allows you to:
- View camera frame information in the terminal
- Save test frames as image files
- Monitor camera performance

Usage:
    python test_camera.py [--save] [--frames N] [--duration SECONDS]
"""

import sys
import time
import argparse
import cv2
from RobotController import get_robot

def print_frame_info(frame_info, frame_num):
    """Print formatted frame information."""
    if frame_info.get("success"):
        print(f"Frame {frame_num:3d}: ✓ OK | "
              f"Size: {frame_info['width']:4d}x{frame_info['height']:4d} | "
              f"Channels: {frame_info['channels']} | "
              f"Shape: {frame_info['shape']}")
        return True
    else:
        print(f"Frame {frame_num:3d}: ✗ ERROR - {frame_info.get('error', 'Unknown')}")
        return False

def save_frame(robot, filename):
    """Save current camera frame to file."""
    if robot.camera is None or not robot.camera.opened:
        print("Error: Camera not opened")
        return False
    
    ret, frame = robot.camera.read()
    if ret and frame is not None:
        cv2.imwrite(filename, frame)
        print(f"✓ Frame saved to: {filename}")
        return True
    else:
        print("✗ Failed to read frame for saving")
        return False

def test_camera_continuous(duration=10, save_frames=False):
    """Test camera continuously for specified duration."""
    robot = get_robot()
    
    print("="*70)
    print("TonyPi Camera Test")
    print("="*70)
    
    # Open camera
    print("\n[1/4] Opening camera...")
    result = robot.camera_open()
    if not result.get("success"):
        print(f"✗ Failed to open camera: {result.get('error')}")
        return
    print("✓ Camera opened successfully")
    time.sleep(1)  # Give camera time to initialize
    
    # Get initial frame info
    print("\n[2/4] Testing frame capture...")
    frame_info = robot.get_camera_frame()
    if not frame_info.get("success"):
        print(f"✗ Failed to read frame: {frame_info.get('error')}")
        robot.camera_close()
        return
    
    print(f"✓ Frame capture working")
    print(f"  Resolution: {frame_info['width']}x{frame_info['height']}")
    print(f"  Channels: {frame_info['channels']}")
    
    # Continuous reading
    print(f"\n[3/4] Reading frames for {duration} seconds...")
    print("-"*70)
    print(f"{'Frame':<8} {'Status':<10} {'Size':<15} {'Channels':<10} {'Shape'}")
    print("-"*70)
    
    start_time = time.time()
    frame_count = 0
    success_count = 0
    
    try:
        while time.time() - start_time < duration:
            frame_info = robot.get_camera_frame()
            frame_count += 1
            
            if print_frame_info(frame_info, frame_count):
                success_count += 1
            
            # Save first frame if requested
            if save_frames and frame_count == 1:
                save_frame(robot, "test_frame_001.jpg")
            
            time.sleep(0.1)  # ~10 FPS display rate
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    # Statistics
    elapsed = time.time() - start_time
    fps = frame_count / elapsed if elapsed > 0 else 0
    success_rate = (success_count / frame_count * 100) if frame_count > 0 else 0
    
    print("-"*70)
    print(f"\nStatistics:")
    print(f"  Total frames: {frame_count}")
    print(f"  Successful: {success_count} ({success_rate:.1f}%)")
    print(f"  Duration: {elapsed:.2f} seconds")
    print(f"  Average FPS: {fps:.2f}")
    
    # Save final frame
    if save_frames:
        print("\n[4/4] Saving final frame...")
        save_frame(robot, "test_frame_final.jpg")
    
    # Close camera
    print("\nClosing camera...")
    result = robot.camera_close()
    if result.get("success"):
        print("✓ Camera closed successfully")
    else:
        print(f"✗ Error closing camera: {result.get('error')}")
    
    print("\n" + "="*70)
    print("Camera test complete!")
    print("="*70)

def test_camera_single_frame():
    """Test camera with a single frame capture and save."""
    robot = get_robot()
    
    print("="*70)
    print("TonyPi Camera Single Frame Test")
    print("="*70)
    
    # Open camera
    print("\nOpening camera...")
    result = robot.camera_open()
    if not result.get("success"):
        print(f"✗ Failed to open camera: {result.get('error')}")
        return
    print("✓ Camera opened")
    time.sleep(1)
    
    # Read frame
    print("\nReading frame...")
    frame_info = robot.get_camera_frame()
    if not frame_info.get("success"):
        print(f"✗ Failed to read frame: {frame_info.get('error')}")
        robot.camera_close()
        return
    
    print("✓ Frame captured successfully")
    print(f"\nFrame Information:")
    print(f"  Width: {frame_info['width']} pixels")
    print(f"  Height: {frame_info['height']} pixels")
    print(f"  Channels: {frame_info['channels']}")
    print(f"  Shape: {frame_info['shape']}")
    
    # Save frame
    print("\nSaving frame to 'camera_test.jpg'...")
    if save_frame(robot, "camera_test.jpg"):
        print("✓ You can view the image with:")
        print("  - Image viewer: xdg-open camera_test.jpg")
        print("  - Or transfer to another computer to view")
    
    # Close camera
    print("\nClosing camera...")
    robot.camera_close()
    print("✓ Test complete!")

def main():
    parser = argparse.ArgumentParser(description='Test TonyPi robot camera')
    parser.add_argument('--save', action='store_true', 
                       help='Save test frames as image files')
    parser.add_argument('--duration', type=int, default=10,
                       help='Duration to test camera in seconds (default: 10)')
    parser.add_argument('--single', action='store_true',
                       help='Test single frame capture only')
    parser.add_argument('--frames', type=int, default=10,
                       help='Number of frames to test (for single mode)')
    
    args = parser.parse_args()
    
    try:
        if args.single:
            test_camera_single_frame()
        else:
            test_camera_continuous(duration=args.duration, save_frames=args.save)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

