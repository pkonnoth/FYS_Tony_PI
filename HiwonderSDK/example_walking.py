#!/usr/bin/env python3
# encoding: utf-8
"""
Quick example showing how to use preprogrammed walking and movement actions

This demonstrates:
- Basic walking (forward, backward)
- Turning
- Continuous walking with stop control
"""

import sys
import time
import threading
import os
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Find the correct action groups path
def find_action_groups_path():
    """Find where action group files are located"""
    possible_paths = [
        '/home/pi/TonyPi/ActionGroups/',
        '/home/pi/one/tonypi_pro/TonyPi/ActionGroups/',
        '/home/pi/tonypi_pro/TonyPi/ActionGroups/',
    ]
    
    for path in possible_paths:
        test_file = os.path.join(path, 'go_forward.d6a')
        if os.path.exists(test_file):
            print(f"Found action groups at: {path}")
            return path
    
    # Default path
    default_path = '/home/pi/TonyPi/ActionGroups/'
    print(f"Warning: Action groups not found in expected locations. Using default: {default_path}")
    return default_path

# Get the correct path
ACTION_GROUPS_PATH = find_action_groups_path()

def run_action(action_name, times=1, with_stand=False):
    """Helper function to run actions with the correct path"""
    return AGC.runActionGroup(action_name, times=times, with_stand=with_stand, 
                            path=ACTION_GROUPS_PATH)

def main():
    # Initialize robot
    print("Initializing robot...")
    board = rrc.Board()
    ctl = Controller(board)
    ctl.enable_recv()
    
    # Center head
    ctl.set_pwm_servo_pulse(1, 1500, 500)
    ctl.set_pwm_servo_pulse(2, 1500, 500)
    time.sleep(0.5)
    
    # Stand first (always good practice)
    print("Standing...")
    run_action('stand_slow', times=1)
    time.sleep(2)
    
    # ========================================
    # Example 1: Basic Walking
    # ========================================
    print("\n" + "="*50)
    print("Example 1: Basic Walking Forward")
    print("="*50)
    
    print("Walking forward 5 steps...")
    run_action('go_forward', times=5, with_stand=True)
    time.sleep(1)
    
    # ========================================
    # Example 2: Walking Backward
    # ========================================
    print("\n" + "="*50)
    print("Example 2: Walking Backward")
    print("="*50)
    
    print("Walking backward 3 steps...")
    run_action('back', times=3, with_stand=True)
    time.sleep(1)
    
    # ========================================
    # Example 3: Turning
    # ========================================
    print("\n" + "="*50)
    print("Example 3: Turning")
    print("="*50)
    
    print("Turning right...")
    run_action('turn_right', times=1)
    time.sleep(1)
    
    print("Turning left...")
    run_action('turn_left', times=1)
    time.sleep(1)
    
    # ========================================
    # Example 4: Different Walk Speeds
    # ========================================
    print("\n" + "="*50)
    print("Example 4: Different Walk Speeds")
    print("="*50)
    
    print("Walking slow...")
    run_action('go_forward_slow', times=3, with_stand=True)
    time.sleep(1)
    
    print("Walking fast...")
    run_action('go_forward_fast', times=3, with_stand=True)
    time.sleep(1)
    
    # ========================================
    # Example 5: Side Movement
    # ========================================
    print("\n" + "="*50)
    print("Example 5: Side Movement")
    print("="*50)
    
    print("Moving left...")
    run_action('left_move', times=2)
    time.sleep(1)
    
    print("Moving right...")
    run_action('right_move', times=2)
    time.sleep(1)
    
    # ========================================
    # Example 6: Continuous Walking (Advanced)
    # ========================================
    print("\n" + "="*50)
    print("Example 6: Continuous Walking with Stop")
    print("="*50)
    
    print("Starting continuous walk (will walk for 5 seconds)...")
    
    # Start walking in a separate thread (non-blocking)
    walk_thread = threading.Thread(
        target=AGC.runActionGroup,
        args=('go_forward', 0, True, '', ACTION_GROUPS_PATH),  # 0 = infinite loop
        daemon=True
    )
    walk_thread.start()
    
    # Let it walk for 5 seconds
    for i in range(5, 0, -1):
        print(f"  Walking... {i} seconds remaining")
        time.sleep(1)
    
    # Stop the walking
    print("Stopping walk...")
    AGC.stopActionGroup()
    time.sleep(1)
    
    # ========================================
    # Example 7: Walking Pattern
    # ========================================
    print("\n" + "="*50)
    print("Example 7: Walking Pattern (Square)")
    print("="*50)
    
    print("Walking in a square pattern...")
    
    # Forward
    print("  Step 1: Forward")
    run_action('go_forward', times=2, with_stand=True)
    time.sleep(0.5)
    
    # Turn right
    print("  Step 2: Turn right")
    run_action('turn_right', times=1)
    time.sleep(0.5)
    
    # Forward
    print("  Step 3: Forward")
    run_action('go_forward', times=2, with_stand=True)
    time.sleep(0.5)
    
    # Turn right
    print("  Step 4: Turn right")
    run_action('turn_right', times=1)
    time.sleep(0.5)
    
    # Forward
    print("  Step 5: Forward")
    run_action('go_forward', times=2, with_stand=True)
    time.sleep(0.5)
    
    # Turn right
    print("  Step 6: Turn right")
    run_action('turn_right', times=1)
    time.sleep(0.5)
    
    # Forward
    print("  Step 7: Forward")
    run_action('go_forward', times=2, with_stand=True)
    time.sleep(0.5)
    
    # Turn right (back to start)
    print("  Step 8: Turn right (back to start)")
    run_action('turn_right', times=1)
    time.sleep(0.5)
    
    print("Square pattern complete!")
    
    # ========================================
    # Cleanup
    # ========================================
    print("\n" + "="*50)
    print("Returning to stand position")
    print("="*50)
    
    run_action('stand_slow', times=1)
    time.sleep(1)
    
    print("\nAll walking examples complete!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Stopping all actions and shutting down...")
        try:
            # Stop any running actions
            AGC.stopActionGroup()
            time.sleep(0.5)
            
            # Return to safe position
            board = rrc.Board()
            ctl = Controller(board)
            ctl.set_pwm_servo_pulse(1, 1500, 500)
            ctl.set_pwm_servo_pulse(2, 1500, 500)
            AGC.runActionGroup('stand_slow', times=1, path=ACTION_GROUPS_PATH)
        except:
            pass
        print("Shutdown complete.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

