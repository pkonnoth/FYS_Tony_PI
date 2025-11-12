# Hiwonder SDK Custom Control Guide

This guide explains how to write custom control programs for your Hiwonder robot using the provided SDK.

## Table of Contents
1. [Basic Setup and Initialization](#basic-setup-and-initialization)
2. [Bus Servo Control](#bus-servo-control)
3. [PWM Servo Control](#pwm-servo-control)
4. [Reading Servo Information](#reading-servo-information)
5. [Action Groups](#action-groups)
6. [Camera Control](#camera-control)
7. [Sensors and Utilities](#sensors-and-utilities)
8. [Example: Complete Custom Control Script](#example-complete-custom-control-script)

---

## Basic Setup and Initialization

### 1. Import Required Modules

```python
import sys
import time
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
from hiwonder.Camera import Camera
```

### 2. Initialize the Board and Controller

```python
# Create board instance (handles serial communication)
board = rrc.Board()

# Create controller instance (high-level API)
ctl = Controller(board)

# Enable data reception (required for reading sensors/servos)
ctl.enable_recv()
```

**Note:** The `Board` class handles low-level serial communication with `/dev/ttyAMA0` at 1000000 baud. The `Controller` class provides a higher-level API with timeout handling.

---

## Bus Servo Control

Bus servos are used for the robot's body joints (typically servos 1-16).

### Set Bus Servo Position

```python
ctl.set_bus_servo_pulse(servo_id, pulse, use_time)
```

**Parameters:**
- `servo_id` (int): Servo ID (1-16)
- `pulse` (int): Target position in pulse width (typically 0-500, but check servo specs)
- `use_time` (int): Time in milliseconds for the servo to reach the position

**Example:**
```python
# Move servo 1 to position 250 over 500ms
ctl.set_bus_servo_pulse(1, 250, 500)

# Move multiple servos sequentially
ctl.set_bus_servo_pulse(1, 250, 500)
time.sleep(0.5)
ctl.set_bus_servo_pulse(2, 250, 500)
time.sleep(0.5)
ctl.set_bus_servo_pulse(3, 250, 500)
```

### Read Bus Servo Position

```python
position = ctl.get_bus_servo_pulse(servo_id)
# Returns: int (pulse position) or None if timeout
```

### Configure Bus Servos

```python
# Set servo deviation (offset calibration)
ctl.set_bus_servo_deviation(servo_id, deviation)  # deviation: -125 to 125
ctl.save_bus_servo_deviation(servo_id)  # Save permanently

# Set angle limits
ctl.set_bus_servo_angle_limit(servo_id, [min_angle, max_angle])

# Set voltage limits (millivolts)
ctl.set_bus_servo_vin_limit(servo_id, [min_voltage, max_voltage])

# Set temperature limit (degrees Celsius)
ctl.set_bus_servo_temp_limit(servo_id, temp_limit)

# Unload servo (disable torque)
ctl.unload_bus_servo(servo_id)
```

### Read Servo Status

```python
# Get current position
position = ctl.get_bus_servo_pulse(servo_id)

# Get voltage (returns in millivolts)
voltage = ctl.get_bus_servo_vin(servo_id)

# Get temperature (returns in degrees Celsius)
temperature = ctl.get_bus_servo_temp(servo_id)

# Get deviation/offset
deviation = ctl.get_bus_servo_deviation(servo_id)
```

---

## PWM Servo Control

PWM servos are typically used for the robot's head (pan-tilt), with IDs 1-4.

### Set PWM Servo Position

```python
ctl.set_pwm_servo_pulse(servo_id, pulse, use_time)
```

**Parameters:**
- `servo_id` (int): Servo ID (1 or 2 for head servos)
- `pulse` (int): Target position in microseconds (typically 500-2500, 1500 = center)
- `use_time` (int): Time in milliseconds for the servo to reach the position

**Example:**
```python
# Center the head (servo 1 is typically pan, servo 2 is tilt)
ctl.set_pwm_servo_pulse(1, 1500, 500)  # Center pan
ctl.set_pwm_servo_pulse(2, 1500, 500)  # Center tilt

# Nod head (move tilt servo up and down)
ctl.set_pwm_servo_pulse(2, 1800, 200)  # Look up
time.sleep(0.2)
ctl.set_pwm_servo_pulse(2, 1200, 200)  # Look down
time.sleep(0.2)
ctl.set_pwm_servo_pulse(2, 1500, 200)  # Center
```

---

## Reading Servo Information

The Controller class provides several methods to read servo state (with automatic retry and timeout):

```python
# Bus servo readings
position = ctl.get_bus_servo_pulse(servo_id)
voltage = ctl.get_bus_servo_vin(servo_id)
temperature = ctl.get_bus_servo_temp(servo_id)
deviation = ctl.get_bus_servo_deviation(servo_id)
angle_limit = ctl.get_bus_servo_angle_limit(servo_id)
vin_limit = ctl.get_bus_servo_vin_limit(servo_id)
temp_limit = ctl.get_bus_servo_temp_limit(servo_id)
servo_id_read = ctl.get_bus_servo_id()  # Read servo ID
```

All read methods return `None` if the operation times out (default timeout: 50 attempts × 0.01s = 0.5s).

---

## Action Groups

Action groups are pre-recorded motion sequences stored as `.d6a` files in `/home/pi/TonyPi/ActionGroups/`.

### Run a Single Action

```python
import hiwonder.ActionGroupControl as AGC

# Run action once
AGC.runAction('stand_slow', lock_servos='', path="/home/pi/TonyPi/ActionGroups/")
```

### Run Action Group with Options

```python
AGC.runActionGroup(actName, times=1, with_stand=False, lock_servos='', path="/home/pi/TonyPi/ActionGroups/")
```

**Parameters:**
- `actName` (str): Action name (without .d6a extension)
- `times` (int): Number of times to repeat (use -1 for infinite)
- `with_stand` (bool): Whether to end with standing action
- `lock_servos` (dict/str): Servos to lock at specific positions: `{'1': 250, '3': 300}`
- `path` (str): Path to action group directory

**Example:**
```python
# Run walk forward 5 times
AGC.runActionGroup('go_forward', times=5, with_stand=True)

# Run action with locked servos
AGC.runActionGroup('stand', times=1, lock_servos={'1': 250})
```

### Stop Actions

```python
from hiwonder.ActionGroupControl import stopAction, stopActionGroup

# Stop current single action
stopAction()

# Stop current action group
stopActionGroup()
```

---

## Camera Control

The Camera class provides USB camera access with threading.

### Initialize and Use Camera

```python
from hiwonder.Camera import Camera

# Create camera instance (default resolution 640x480)
my_camera = Camera(resolution=(640, 480))

# Open camera
my_camera.camera_open()

# Read frame in main loop
while True:
    ret, frame = my_camera.read()
    if ret and frame is not None:
        # Process frame (OpenCV)
        cv2.imshow('frame', frame)
        # Your image processing code here
    time.sleep(0.01)

# Close camera when done
my_camera.camera_close()
```

**Note:** Camera settings are loaded from `/boot/camera_setting.yaml` (flip settings).

---

## Sensors and Utilities

### IMU (Inertial Measurement Unit)

```python
# Get IMU data: ax, ay, az, gx, gy, gz
imu_data = ctl.get_imu()
if imu_data is not None:
    ax, ay, az, gx, gy, gz = imu_data
    # ax, ay, az: accelerometer (m/s²)
    # gx, gy, gz: gyroscope (rad/s)
```

### Buzzer Control

```python
ctl.set_buzzer(freq, on_time, off_time, repeat=1)
```

**Parameters:**
- `freq` (int): Frequency in Hz
- `on_time` (float): On duration in seconds
- `off_time` (float): Off duration in seconds
- `repeat` (int): Number of repetitions

**Example:**
```python
# Beep at 1900Hz for 0.1s, pause 0.9s, repeat once
ctl.set_buzzer(1900, 0.1, 0.9, 1)
```

### Low-Level Board Access

For advanced control, you can access the `board` object directly:

```python
# Motor control
board.set_motor_speed([[motor_id, speed], ...])  # speed: -1.0 to 1.0
board.set_motor_duty([[motor_id, duty], ...])    # duty: percentage

# LED control
board.set_led(on_time, off_time, repeat=1, led_id=1)

# RGB LED control
board.set_rgb([[index, r, g, b], ...])

# OLED display
board.set_oled_text(line, text)

# Get button press
button_data = board.get_button()  # Returns (key_id, event) or None

# Get gamepad input
gamepad_data = board.get_gamepad()  # Returns (axes, buttons) or None

# Get battery voltage
battery = board.get_battery()  # Returns voltage in millivolts or None
```

---

## Example: Complete Custom Control Script

Here's a complete example that demonstrates custom robot control:

```python
#!/usr/bin/env python3
# encoding: utf-8
import sys
import time
import cv2
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
from hiwonder.Camera import Camera

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Initialize
board = rrc.Board()
ctl = Controller(board)
ctl.enable_recv()

# Initialize camera
camera = Camera()
camera.camera_open()

# Initialization sequence
print("Initializing robot...")
ctl.set_pwm_servo_pulse(1, 1500, 500)  # Center pan
ctl.set_pwm_servo_pulse(2, 1500, 500)  # Center tilt
time.sleep(0.5)

# Run stand action
AGC.runActionGroup('stand_slow', times=1)
time.sleep(2)

# Beep to indicate ready
ctl.set_buzzer(1900, 0.1, 0.9, 1)
print("Robot ready!")

def custom_walk_sequence():
    """Custom walking sequence"""
    print("Starting custom walk...")
    AGC.runActionGroup('go_forward', times=3, with_stand=True)
    time.sleep(1)
    AGC.runActionGroup('back', times=2, with_stand=True)
    time.sleep(1)

def head_movement():
    """Custom head movement"""
    print("Moving head...")
    # Look left
    ctl.set_pwm_servo_pulse(1, 1200, 300)
    time.sleep(0.3)
    # Look right
    ctl.set_pwm_servo_pulse(1, 1800, 300)
    time.sleep(0.3)
    # Center
    ctl.set_pwm_servo_pulse(1, 1500, 300)
    time.sleep(0.3)
    # Look up
    ctl.set_pwm_servo_pulse(2, 1800, 300)
    time.sleep(0.3)
    # Look down
    ctl.set_pwm_servo_pulse(2, 1200, 300)
    time.sleep(0.3)
    # Center
    ctl.set_pwm_servo_pulse(2, 1500, 300)
    time.sleep(0.3)

def monitor_servos():
    """Monitor servo temperatures"""
    for servo_id in range(1, 17):
        temp = ctl.get_bus_servo_temp(servo_id)
        if temp is not None:
            print(f"Servo {servo_id} temperature: {temp}°C")
            if temp > 70:  # Warning threshold
                print(f"WARNING: Servo {servo_id} is getting hot!")

try:
    # Main control loop
    print("Starting main control loop...")
    frame_count = 0
    
    while True:
        # Read camera frame
        ret, frame = camera.read()
        if ret and frame is not None:
            frame_count += 1
            
            # Process every 30 frames (1 second at 30fps)
            if frame_count % 30 == 0:
                # Check IMU
                imu_data = ctl.get_imu()
                if imu_data is not None:
                    ax, ay, az, gx, gy, gz = imu_data
                    print(f"IMU - Accel: ({ax:.2f}, {ay:.2f}, {az:.2f}), "
                          f"Gyro: ({gx:.2f}, {gy:.2f}, {gz:.2f})")
                
                # Monitor servos every 5 seconds
                if frame_count % 150 == 0:
                    monitor_servos()
        
        # Example: Run actions based on conditions
        # (Add your control logic here)
        
        time.sleep(0.01)  # Small delay to prevent CPU overload

except KeyboardInterrupt:
    print("\nShutting down...")
    # Cleanup
    AGC.runActionGroup('stand_slow', times=1)
    time.sleep(1)
    ctl.set_pwm_servo_pulse(1, 1500, 500)
    ctl.set_pwm_servo_pulse(2, 1500, 500)
    camera.camera_close()
    print("Shutdown complete.")
```

---

## Key Points for Custom Control

1. **Always initialize:** Call `ctl.enable_recv()` before reading sensor data
2. **Use delays:** Add appropriate `time.sleep()` between servo movements
3. **Check return values:** Servo read operations can return `None` on timeout
4. **Action groups vs direct control:**
   - Use **action groups** for pre-recorded complex movements
   - Use **direct servo control** for precise, custom movements
5. **Servo IDs:**
   - Bus servos: 1-16 (robot body joints)
   - PWM servos: 1-2 (typically head pan-tilt)
6. **Thread safety:** The SDK uses threading internally, but be careful with multiple simultaneous operations

---

## Troubleshooting

1. **Servo not responding:**
   - Check if `ctl.enable_recv()` was called
   - Verify servo ID is correct
   - Check servo temperature and voltage limits

2. **Read operations returning None:**
   - Increase timeout in Controller initialization: `ctl = Controller(board, time_out=100)`
   - Ensure serial connection is stable

3. **Camera not working:**
   - Check camera permissions
   - Verify camera settings in `/boot/camera_setting.yaml`

4. **Action groups not found:**
   - Verify action files exist in `/home/pi/TonyPi/ActionGroups/`
   - Check file permissions

---

## Additional Resources

- Check example files in `/home/pi/TonyPi/Functions/` for more patterns
- Look at `RPCServer.py` for remote control examples
- Review `ActionGroupControl.py` for action group implementation details

