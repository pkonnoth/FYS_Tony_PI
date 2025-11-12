#!/usr/bin/env python3
# encoding: utf-8
"""
TonyPi Robot Control Class for MCP Server Integration

This class provides a comprehensive interface to control the TonyPi robot,
wrapping all available functionality including:
- Action groups (pre-programmed movements)
- Servo control (bus and PWM)
- Sensor reading (IMU, battery, buttons)
- Camera access
- Buzzer and LED control
- Motor control

All methods are designed to be MCP tool-callable with proper type hints.
"""

import sys
import time
import threading
import os
from typing import Dict, List, Optional, Tuple, Any
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
from hiwonder.Camera import Camera

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)


class RobotController:
    """
    Main robot control class for TonyPi robot.
    
    This class provides a unified interface to all robot capabilities,
    designed to be easily exposed via MCP server for AI/LLM control.
    """
    
    def __init__(self):
        """Initialize the robot controller."""
        self.board = rrc.Board()
        self.controller = Controller(self.board)
        self.controller.enable_recv()
        self.camera = None
        self._action_thread = None
        self._is_initialized = True
        
        # Find action groups path
        self._action_path = self._find_action_groups_path()
        
        print(f"[RobotController] Initialized. Action groups path: {self._action_path}")
    
    def _find_action_groups_path(self) -> str:
        """Find where action group files are located."""
        possible_paths = [
            '/home/pi/TonyPi/ActionGroups/',
            '/home/pi/one/tonypi_pro/TonyPi/ActionGroups/',
            '/home/pi/tonypi_pro/TonyPi/ActionGroups/',
        ]
        
        for path in possible_paths:
            test_file = os.path.join(path, 'go_forward.d6a')
            if os.path.exists(test_file):
                return path
        
        default_path = '/home/pi/TonyPi/ActionGroups/'
        print(f"[RobotController] Warning: Action groups not found. Using default: {default_path}")
        return default_path
    
    # ============================================================================
    # ACTION GROUP METHODS (Pre-programmed Movements)
    # ============================================================================
    
    def run_action(self, action_name: str, times: int = 1, with_stand: bool = False) -> Dict[str, Any]:
        """
        Run a pre-programmed action group.
        
        Args:
            action_name: Name of the action (e.g., 'go_forward', 'wave', 'stand')
            times: Number of times to repeat (1 = once, 0 = infinite loop)
            with_stand: If True, ends with standing action for stability
            
        Returns:
            Dict with success status and message
        """
        try:
            AGC.runActionGroup(action_name, times=times, with_stand=with_stand, path=self._action_path)
            return {"success": True, "message": f"Action '{action_name}' started"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def run_action_async(self, action_name: str, times: int = 1, with_stand: bool = False) -> Dict[str, Any]:
        """
        Run an action group asynchronously (non-blocking).
        
        Args:
            action_name: Name of the action
            times: Number of times to repeat (0 = infinite loop)
            with_stand: If True, ends with standing action
            
        Returns:
            Dict with success status
        """
        try:
            if self._action_thread is not None and self._action_thread.is_alive():
                return {"success": False, "error": "Another action is already running"}
            
            self._action_thread = threading.Thread(
                target=AGC.runActionGroup,
                args=(action_name, times, with_stand, '', self._action_path),
                daemon=True
            )
            self._action_thread.start()
            return {"success": True, "message": f"Action '{action_name}' started in background"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_action(self) -> Dict[str, Any]:
        """
        Stop the currently running action group.
        
        Returns:
            Dict with success status
        """
        try:
            AGC.stopActionGroup()
            return {"success": True, "message": "Action stopped"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Movement Actions
    def walk_forward(self, steps: int = 1, speed: str = "normal", with_stand: bool = True) -> Dict[str, Any]:
        """
        Walk forward.
        
        Args:
            steps: Number of steps to take
            speed: 'slow', 'normal', or 'fast'
            with_stand: End in standing position
            
        Returns:
            Dict with success status
        """
        action_map = {
            'slow': 'go_forward_slow',
            'normal': 'go_forward',
            'fast': 'go_forward_fast'
        }
        action = action_map.get(speed, 'go_forward')
        return self.run_action(action, times=steps, with_stand=with_stand)
    
    def walk_backward(self, steps: int = 1, fast: bool = False, with_stand: bool = True) -> Dict[str, Any]:
        """Walk backward."""
        action = 'back_fast' if fast else 'back'
        return self.run_action(action, times=steps, with_stand=with_stand)
    
    def turn_left(self, times: int = 1) -> Dict[str, Any]:
        """Turn left."""
        return self.run_action('turn_left', times=times)
    
    def turn_right(self, times: int = 1) -> Dict[str, Any]:
        """Turn right."""
        return self.run_action('turn_right', times=times)
    
    def move_left(self, steps: int = 1, fast: bool = False) -> Dict[str, Any]:
        """Move left."""
        action = 'left_move_fast' if fast else 'left_move'
        return self.run_action(action, times=steps)
    
    def move_right(self, steps: int = 1, fast: bool = False) -> Dict[str, Any]:
        """Move right."""
        action = 'right_move_fast' if fast else 'right_move'
        return self.run_action(action, times=steps)
    
    # Posture Actions
    def stand(self, slow: bool = True) -> Dict[str, Any]:
        """Stand at attention."""
        action = 'stand_slow' if slow else 'stand'
        return self.run_action(action, times=1)
    
    def step_in_place(self, times: int = 10) -> Dict[str, Any]:
        """March in place."""
        return self.run_action('stepping', times=times)
    
    # Gesture Actions
    def wave(self, times: int = 3) -> Dict[str, Any]:
        """Wave hand."""
        return self.run_action('wave', times=times)
    
    def bow(self, times: int = 1) -> Dict[str, Any]:
        """Bow."""
        return self.run_action('bow', times=times)
    
    def celebrate(self) -> Dict[str, Any]:
        """Celebration pose."""
        return self.run_action('chest', times=1)
    
    def twist(self, times: int = 5) -> Dict[str, Any]:
        """Twist waist."""
        return self.run_action('twist', times=times)
    
    # Exercise Actions
    def push_ups(self, times: int = 3) -> Dict[str, Any]:
        """Do push-ups."""
        return self.run_action('push_ups', times=times)
    
    def sit_ups(self, times: int = 3) -> Dict[str, Any]:
        """Do sit-ups."""
        return self.run_action('sit_ups', times=times)
    
    def squat(self, times: int = 5) -> Dict[str, Any]:
        """Squat."""
        return self.run_action('squat', times=times)
    
    def weightlifting(self) -> Dict[str, Any]:
        """Weightlifting pose."""
        return self.run_action('weightlifting', times=1)
    
    # Martial Arts Actions
    def kick_left(self, fast: bool = False) -> Dict[str, Any]:
        """Left kick."""
        action = 'left_shot_fast' if fast else 'left_kick'
        return self.run_action(action, times=1)
    
    def kick_right(self, fast: bool = False) -> Dict[str, Any]:
        """Right kick."""
        action = 'right_shot_fast' if fast else 'right_kick'
        return self.run_action(action, times=1)
    
    def punch_left(self) -> Dict[str, Any]:
        """Left hook punch."""
        return self.run_action('left_uppercut', times=1)
    
    def punch_right(self) -> Dict[str, Any]:
        """Right hook punch."""
        return self.run_action('right_uppercut', times=1)
    
    def wing_chun(self) -> Dict[str, Any]:
        """Wing Chun martial arts moves."""
        return self.run_action('wing_chun', times=1)
    
    # Recovery Actions
    def stand_up_from_front(self) -> Dict[str, Any]:
        """Stand up from front fall."""
        return self.run_action('stand_up_front', times=1)
    
    def stand_up_from_back(self) -> Dict[str, Any]:
        """Stand up from back fall."""
        return self.run_action('stand_up_back', times=1)
    
    # ============================================================================
    # SERVO CONTROL METHODS
    # ============================================================================
    
    def set_bus_servo(self, servo_id: int, position: int, duration_ms: int = 500) -> Dict[str, Any]:
        """
        Set bus servo position.
        
        Args:
            servo_id: Servo ID (1-18)
            position: Target position (0-500)
            duration_ms: Movement duration in milliseconds
            
        Returns:
            Dict with success status
        """
        try:
            if not (1 <= servo_id <= 18):
                return {"success": False, "error": "Servo ID must be between 1 and 18"}
            if not (0 <= position <= 500):
                return {"success": False, "error": "Position must be between 0 and 500"}
            
            self.controller.set_bus_servo_pulse(servo_id, position, duration_ms)
            return {"success": True, "message": f"Servo {servo_id} set to position {position}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_bus_servo_position(self, servo_id: int) -> Dict[str, Any]:
        """
        Get bus servo current position.
        
        Args:
            servo_id: Servo ID (1-18)
            
        Returns:
            Dict with position or error
        """
        try:
            position = self.controller.get_bus_servo_pulse(servo_id)
            if position is None:
                return {"success": False, "error": "Timeout reading servo position"}
            return {"success": True, "position": position, "servo_id": servo_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_head_pan(self, position: int, duration_ms: int = 500) -> Dict[str, Any]:
        """
        Set head pan (left-right) position.
        
        Args:
            position: Position in microseconds (500-2500, 1500 = center)
            duration_ms: Movement duration
            
        Returns:
            Dict with success status
        """
        try:
            self.controller.set_pwm_servo_pulse(1, position, duration_ms)
            return {"success": True, "message": f"Head pan set to {position}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_head_tilt(self, position: int, duration_ms: int = 500) -> Dict[str, Any]:
        """
        Set head tilt (up-down) position.
        
        Args:
            position: Position in microseconds (500-2500, 1500 = center)
            duration_ms: Movement duration
            
        Returns:
            Dict with success status
        """
        try:
            self.controller.set_pwm_servo_pulse(2, position, duration_ms)
            return {"success": True, "message": f"Head tilt set to {position}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def center_head(self, duration_ms: int = 500) -> Dict[str, Any]:
        """
        Center the head (pan and tilt).
        
        Args:
            duration_ms: Movement duration
            
        Returns:
            Dict with success status
        """
        try:
            self.controller.set_pwm_servo_pulse(1, 1500, duration_ms)
            self.controller.set_pwm_servo_pulse(2, 1500, duration_ms)
            return {"success": True, "message": "Head centered"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def look_at(self, pan: int, tilt: int, duration_ms: int = 500) -> Dict[str, Any]:
        """
        Set head to look at specific pan/tilt position.
        
        Args:
            pan: Pan position (500-2500, 1500 = center)
            tilt: Tilt position (500-2500, 1500 = center)
            duration_ms: Movement duration
            
        Returns:
            Dict with success status
        """
        try:
            self.controller.set_pwm_servo_pulse(1, pan, duration_ms)
            self.controller.set_pwm_servo_pulse(2, tilt, duration_ms)
            return {"success": True, "message": f"Head looking at pan={pan}, tilt={tilt}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_servo_temperature(self, servo_id: int) -> Dict[str, Any]:
        """
        Get bus servo temperature.
        
        Args:
            servo_id: Servo ID (1-18)
            
        Returns:
            Dict with temperature in Celsius
        """
        try:
            temp = self.controller.get_bus_servo_temp(servo_id)
            if temp is None:
                return {"success": False, "error": "Timeout reading servo temperature"}
            return {"success": True, "temperature": temp, "servo_id": servo_id, "unit": "celsius"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_servo_voltage(self, servo_id: int) -> Dict[str, Any]:
        """
        Get bus servo voltage.
        
        Args:
            servo_id: Servo ID (1-18)
            
        Returns:
            Dict with voltage in millivolts
        """
        try:
            voltage = self.controller.get_bus_servo_vin(servo_id)
            if voltage is None:
                return {"success": False, "error": "Timeout reading servo voltage"}
            return {"success": True, "voltage": voltage, "servo_id": servo_id, "unit": "millivolts"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # SENSOR METHODS
    # ============================================================================
    
    def get_imu(self) -> Dict[str, Any]:
        """
        Get IMU (Inertial Measurement Unit) data.
        
        Returns:
            Dict with accelerometer and gyroscope data:
            - ax, ay, az: Accelerometer (m/s²)
            - gx, gy, gz: Gyroscope (rad/s)
        """
        try:
            data = self.controller.get_imu()
            if data is None:
                return {"success": False, "error": "Timeout reading IMU"}
            
            ax, ay, az, gx, gy, gz = data
            return {
                "success": True,
                "accelerometer": {
                    "x": ax,
                    "y": ay,
                    "z": az,
                    "unit": "m/s²"
                },
                "gyroscope": {
                    "x": gx,
                    "y": gy,
                    "z": gz,
                    "unit": "rad/s"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_battery_voltage(self) -> Dict[str, Any]:
        """
        Get battery voltage.
        
        Returns:
            Dict with battery voltage in millivolts
        """
        try:
            voltage = self.board.get_battery()
            if voltage is None:
                return {"success": False, "error": "Timeout reading battery voltage"}
            return {"success": True, "voltage": voltage, "unit": "millivolts"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # CAMERA METHODS
    # ============================================================================
    
    def camera_open(self) -> Dict[str, Any]:
        """
        Open the camera.
        
        Returns:
            Dict with success status
        """
        try:
            if self.camera is None:
                self.camera = Camera()
            self.camera.camera_open()
            time.sleep(0.5)  # Give camera time to initialize
            return {"success": True, "message": "Camera opened"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def camera_close(self) -> Dict[str, Any]:
        """
        Close the camera.
        
        Returns:
            Dict with success status
        """
        try:
            if self.camera is not None:
                self.camera.camera_close()
            return {"success": True, "message": "Camera closed"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_camera_frame(self) -> Dict[str, Any]:
        """
        Get current camera frame.
        
        Returns:
            Dict with frame information (shape, available status)
            Note: For MCP, you may want to encode the frame as base64
        """
        try:
            if self.camera is None:
                return {"success": False, "error": "Camera not opened"}
            
            ret, frame = self.camera.read()
            if not ret or frame is None:
                return {"success": False, "error": "No frame available"}
            
            return {
                "success": True,
                "frame_available": True,
                "shape": frame.shape,
                "width": frame.shape[1],
                "height": frame.shape[0],
                "channels": frame.shape[2] if len(frame.shape) > 2 else 1
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # BUZZER AND LED METHODS
    # ============================================================================
    
    def beep(self, frequency: int = 1900, on_time: float = 0.1, off_time: float = 0.9, repeat: int = 1) -> Dict[str, Any]:
        """
        Play a beep sound.
        
        Args:
            frequency: Sound frequency in Hz
            on_time: Time buzzer is on (seconds)
            off_time: Time buzzer is off (seconds)
            repeat: Number of repetitions
            
        Returns:
            Dict with success status
        """
        try:
            self.controller.set_buzzer(frequency, on_time, off_time, repeat)
            return {"success": True, "message": f"Beep played: {frequency}Hz, {repeat} times"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get overall robot status.
        
        Returns:
            Dict with robot status information
        """
        try:
            imu_data = self.get_imu()
            battery_data = self.get_battery_voltage()
            
            status = {
                "success": True,
                "initialized": self._is_initialized,
                "action_running": self._action_thread is not None and self._action_thread.is_alive() if self._action_thread else False,
                "camera_opened": self.camera is not None and self.camera.opened if self.camera else False,
                "imu": imu_data if imu_data.get("success") else None,
                "battery": battery_data if battery_data.get("success") else None
            }
            return status
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def shutdown(self) -> Dict[str, Any]:
        """
        Shutdown robot safely (stop actions, center head, stand).
        
        Returns:
            Dict with success status
        """
        try:
            # Stop any running actions
            self.stop_action()
            time.sleep(0.5)
            
            # Center head
            self.center_head()
            time.sleep(0.5)
            
            # Stand
            self.stand()
            
            return {"success": True, "message": "Robot shutdown complete"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance for easy access
_robot_instance = None

def get_robot() -> RobotController:
    """
    Get or create the singleton robot controller instance.
    
    Returns:
        RobotController instance
    """
    global _robot_instance
    if _robot_instance is None:
        _robot_instance = RobotController()
    return _robot_instance


if __name__ == '__main__':
    # Example usage
    robot = get_robot()
    
    print("Testing robot controller...")
    
    # Test status
    status = robot.get_status()
    print(f"Status: {status}")
    
    # Test stand
    print("\nStanding...")
    result = robot.stand()
    print(f"Stand result: {result}")
    time.sleep(2)
    
    # Test walk
    print("\nWalking forward 2 steps...")
    result = robot.walk_forward(steps=2)
    print(f"Walk result: {result}")
    time.sleep(3)
    
    # Test wave
    print("\nWaving...")
    result = robot.wave(times=3)
    print(f"Wave result: {result}")
    time.sleep(3)
    
    # Test IMU
    print("\nReading IMU...")
    imu = robot.get_imu()
    print(f"IMU: {imu}")
    
    print("\nTest complete!")

