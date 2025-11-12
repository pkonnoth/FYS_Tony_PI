#!/usr/bin/env python3
# encoding: utf-8
"""
Simple example demonstrating custom robot control using the Hiwonder SDK

This example shows:
1. Basic initialization
2. Servo control (bus and PWM)
3. Action group usage
4. Sensor reading (IMU)
5. Camera access
"""

import sys
import time
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
from hiwonder.Camera import Camera

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

def main():
    # ========================================
    # STEP 1: Initialize the SDK
    # ========================================
    print("Initializing robot...")
    
    # Create board instance (handles serial communication)
    board = rrc.Board()
    
    # Create controller instance (high-level API)
    ctl = Controller(board)
    
    # Enable data reception (required for reading sensors/servos)
    ctl.enable_recv()
    
    print("Robot initialized!")
    time.sleep(1)
    
    # ========================================
    # STEP 2: Initial Position Setup
    # ========================================
    print("Moving to initial position...")
    
    # Center the head servos (PWM servos)
    ctl.set_pwm_servo_pulse(1, 1500, 500)  # Pan servo (left-right)
    ctl.set_pwm_servo_pulse(2, 1500, 500)  # Tilt servo (up-down)
    time.sleep(0.5)
    
    # Run stand action to get robot in ready position
    print("Running stand action...")
    AGC.runActionGroup('stand_slow', times=1)
    time.sleep(2)
    
    # Beep to indicate ready
    ctl.set_buzzer(1900, 0.1, 0.9, 1)
    print("Robot ready!\n")
    
    # ========================================
    # STEP 3: Example 1 - Direct Servo Control
    # ========================================
    print("=" * 50)
    print("Example 1: Direct Servo Control")
    print("=" * 50)
    
    def simple_head_movement():
        """Move head in a simple pattern"""
        print("Moving head: left -> center -> right -> center")
        
        # Look left
        ctl.set_pwm_servo_pulse(1, 1200, 300)
        time.sleep(1)
        
        # Center
        ctl.set_pwm_servo_pulse(1, 1500, 300)
        time.sleep(1)
        
        # Look right
        ctl.set_pwm_servo_pulse(1, 1800, 300)
        time.sleep(1)
        
        # Center
        ctl.set_pwm_servo_pulse(1, 1500, 300)
        time.sleep(1)
        
        print("Head movement complete.\n")
    
    simple_head_movement()
    time.sleep(1)
    
    # ========================================
    # STEP 4: Example 2 - Reading Servo Information
    # ========================================
    print("=" * 50)
    print("Example 2: Reading Servo Information")
    print("=" * 50)
    
    # Read bus servo positions (example: servos 1-6)
    print("Reading bus servo positions...")
    for servo_id in range(1, 7):
        position = ctl.get_bus_servo_pulse(servo_id)
        if position is not None:
            print(f"  Servo {servo_id} position: {position}")
        else:
            print(f"  Servo {servo_id}: Timeout reading position")
    
    # Read PWM servo positions
    print("\nReading PWM servo positions...")
    # Note: Direct position reading for PWM servos may require low-level access
    print("  PWM servo control available (direct reading via board.pwm_servo_read_position)")
    
    print()
    
    # ========================================
    # STEP 5: Example 3 - Using Action Groups
    # ========================================
    print("=" * 50)
    print("Example 3: Using Action Groups")
    print("=" * 50)
    
    try:
        print("Running 'go_forward' action 2 times...")
        AGC.runActionGroup('go_forward', times=2, with_stand=True)
        print("Action group complete.\n")
    except Exception as e:
        print(f"Error running action group: {e}")
        print("Make sure action group files exist in /home/pi/TonyPi/ActionGroups/\n")
    
    time.sleep(1)
    
    # ========================================
    # STEP 6: Example 4 - Reading IMU Data
    # ========================================
    print("=" * 50)
    print("Example 4: Reading IMU Data")
    print("=" * 50)
    
    print("Reading IMU data (5 samples)...")
    for i in range(5):
        imu_data = ctl.get_imu()
        if imu_data is not None:
            ax, ay, az, gx, gy, gz = imu_data
            print(f"  Sample {i+1}:")
            print(f"    Accelerometer: X={ax:.2f}, Y={ay:.2f}, Z={az:.2f} m/s²")
            print(f"    Gyroscope:     X={gx:.2f}, Y={gy:.2f}, Z={gz:.2f} rad/s")
        else:
            print(f"  Sample {i+1}: Timeout reading IMU")
        time.sleep(0.1)
    
    print()
    
    # ========================================
    # STEP 7: Example 5 - Camera Access
    # ========================================
    print("=" * 50)
    print("Example 5: Camera Access")
    print("=" * 50)
    
    print("Initializing camera...")
    camera = Camera(resolution=(640, 480))
    camera.camera_open()
    time.sleep(1)  # Give camera time to initialize
    
    print("Reading camera frames (10 frames)...")
    for i in range(10):
        ret, frame = camera.read()
        if ret and frame is not None:
            print(f"  Frame {i+1}: OK - Shape: {frame.shape}")
        else:
            print(f"  Frame {i+1}: No frame available")
        time.sleep(0.1)
    
    camera.camera_close()
    print("Camera closed.\n")
    
    # ========================================
    # STEP 8: Example 6 - Servo Temperature Monitoring
    # ========================================
    print("=" * 50)
    print("Example 6: Servo Temperature Monitoring")
    print("=" * 50)
    
    print("Checking servo temperatures...")
    for servo_id in range(1, 7):
        temp = ctl.get_bus_servo_temp(servo_id)
        voltage = ctl.get_bus_servo_vin(servo_id)
        
        if temp is not None:
            print(f"  Servo {servo_id}: Temperature = {temp}°C", end="")
            if temp > 70:
                print(" [WARNING: Hot!]")
            else:
                print()
        else:
            print(f"  Servo {servo_id}: Could not read temperature")
        
        if voltage is not None:
            print(f"            Voltage = {voltage/1000:.2f}V")
    
    print()
    
    # ========================================
    # STEP 9: Cleanup
    # ========================================
    print("=" * 50)
    print("Example Complete - Returning to safe position")
    print("=" * 50)
    
    # Return head to center
    ctl.set_pwm_servo_pulse(1, 1500, 500)
    ctl.set_pwm_servo_pulse(2, 1500, 500)
    time.sleep(0.5)
    
    # Return to stand position
    AGC.runActionGroup('stand_slow', times=1)
    time.sleep(1)
    
    print("\nAll examples complete!")
    print("Robot is in safe position.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Shutting down...")
        # Quick cleanup
        try:
            board = rrc.Board()
            ctl = Controller(board)
            ctl.set_pwm_servo_pulse(1, 1500, 500)
            ctl.set_pwm_servo_pulse(2, 1500, 500)
            AGC.runActionGroup('stand_slow', times=1)
        except:
            pass
        print("Shutdown complete.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

