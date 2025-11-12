# TonyPi Controller Information

## Overview

Based on online research, official documentation, and codebase analysis, here's comprehensive information about the TonyPi controller:

## Official Controller Architecture

### Dual-Core Control System

The TonyPi uses a **dual-core control system**:

1. **Primary Controller: Raspberry Pi 5**
   - High-level processing
   - Image processing (OpenCV)
   - Python programming
   - Camera processing
   - AI/ML applications

2. **Secondary Controller: STM32 Microcontroller**
   - Low-level hardware management
   - Servo control
   - Motor control
   - Sensor reading (IMU, buttons)
   - Peripheral control (LEDs, buzzer, OLED)
   - **Communication:** Serial port at 1 Mbps

## Official Information

### Platform
- **Base Platform:** Raspberry Pi 5 (or Raspberry Pi 4 in older versions)
- **Control System:** Dual-core control system
- **Programming:** Primarily Python with OpenCV

### Controller Board Characteristics

From the SDK code analysis (`ros_robot_controller_sdk.py`):

**1. Communication Interface:**
- **Serial Port:** `/dev/ttyAMA0`
- **Baud Rate:** 1,000,000 bps (1 Mbps)
- **Protocol:** Custom binary packet protocol
- **MCU:** STM32-based (mentioned in SDK header: `# stm32 python sdk`)

**2. Packet Protocol Format:**
```
[0xAA 0x55] [Function Code] [Length] [Data...] [CRC8 Checksum]
```

**3. Supported Functions (from SDK):**
- `PACKET_FUNC_SYS` (0) - System functions
- `PACKET_FUNC_LED` (1) - LED control
- `PACKET_FUNC_BUZZER` (2) - Buzzer control
- `PACKET_FUNC_MOTOR` (3) - Motor control (4 motors)
- `PACKET_FUNC_PWM_SERVO` (4) - PWM servo control (servos 1-4, typically head pan/tilt)
- `PACKET_FUNC_BUS_SERVO` (5) - Bus servo control (servos 1-18, body joints)
- `PACKET_FUNC_KEY` (6) - Button/key reading
- `PACKET_FUNC_IMU` (7) - IMU sensor (6-axis: ax, ay, az, gx, gy, gz)
- `PACKET_FUNC_GAMEPAD` (8) - Gamepad input
- `PACKET_FUNC_SBUS` (9) - SBus receiver (RC model aircraft protocol)
- `PACKET_FUNC_OLED` (10) - OLED display control
- `PACKET_FUNC_RGB` (11) - RGB LED control

## Hardware Capabilities

### Servos
- **Bus Servos:** Up to 18 servos (body joints)
  - Position range: 0-500 (pulse width units)
  - Can read: position, temperature, voltage, deviation, limits
  - Can set: position, limits, offset, ID
  - Control via: `bus_servo_set_position()`

- **PWM Servos:** 4 servos (typically head/pan-tilt)
  - Position range: 500-2500 microseconds (1500 = center)
  - Servos 1-2 typically used for head (pan/tilt)

### Sensors
- **IMU (Inertial Measurement Unit):**
  - 3-axis accelerometer (ax, ay, az) in m/s²
  - 3-axis gyroscope (gx, gy, gz) in rad/s
  - Accessed via: `board.get_imu()`

- **Buttons/Keys:**
  - Multiple button events supported
  - Click, double-click, triple-click, long press
  - Accessed via: `board.get_button()`

- **Battery Voltage:**
  - Can read battery voltage in millivolts
  - Accessed via: `board.get_battery()`

### Actuators
- **Motors:** 4 motors supported
  - Speed control: `-1.0` to `1.0`
  - Duty cycle control: percentage
  - Accessed via: `board.set_motor_speed()` or `board.set_motor_duty()`

- **LEDs:** Onboard LED control
- **Buzzer:** Programmable buzzer with frequency control
- **OLED Display:** Text display capability
- **RGB LEDs:** Multi-pixel RGB LED control

### Camera
- **Type:** USB camera
- **Resolution:** Configurable (default 640x480)
- **Features:** 2-DOF (degrees of freedom) - pan and tilt
- **Software:** OpenCV-based camera interface
- **Config:** `/boot/camera_setting.yaml`

## Control Interfaces

### 1. Serial Communication (Primary)
- Direct serial communication with STM32 board
- 1 Mbps high-speed serial
- Used by SDK for all hardware control

### 2. Mobile App (Official)
- Wireless control via dedicated Hiwonder mobile app
- Features: Model control, auto shooting, color recognition, line following, etc.

### 3. Wireless Handle (Optional)
- USB handle receiver
- Gamepad-style wireless control
- SBus protocol support

### 4. Python SDK (Development)
- Custom Python SDK (`hiwonder` package)
- Open-source code provided by Hiwonder
- Direct hardware access

## Official Documentation & Resources

### Official Documentation Links
- **Main Documentation:** https://docs.hiwonder.com/projects/TonyPi_Pro/
- **Wiki Documentation:** https://wiki.hiwonder.com/projects/TonyPi_Pro/
- **Quick Start Guide:** https://docs.hiwonder.com/projects/TonyPi/en/latest/docs/2.quick_user_experience.html

### Available Resources
- **Open-Source Python Code:** Provided by Hiwonder
- **Comprehensive Tutorials:** Sensor integration, AI courses, application development
- **Mobile App:** Dedicated Hiwonder app for robot control
- **Development SDK:** Python SDK with libraries and examples

### Key Documentation Areas
1. Getting Started guides
2. Sensor development courses
3. AI voice interaction
4. Custom application development
5. Open-source Python code examples

## Protocol Details (From Code)

### Checksum Algorithm
- **Type:** CRC8
- **Table:** Provided in SDK (256-byte lookup table)
- **Function:** `checksum_crc8(data)` - calculates checksum for packet validation

### Packet Structure
```python
# Sending packet
buf = [0xAA, 0x55, function_code, length]
buf.extend(data)
buf.append(checksum_crc8(buf[2:]))

# Receiving packet
# State machine parsing:
# 1. Wait for 0xAA (start byte 1)
# 2. Wait for 0x55 (start byte 2)
# 3. Read function code
# 4. Read length
# 5. Read data (length bytes)
# 6. Read and verify checksum
```

### Bus Servo Control Example
```python
# Set servo position
# Packet: [0xAA, 0x55, 0x05, length, 0x01, duration_low, duration_high, count, [servo_id, pulse]..., checksum]
# Function: PACKET_FUNC_BUS_SERVO (0x05)
# Sub-command: 0x01 (set position)
# Duration: 2 bytes (low, high) in milliseconds
# Positions: List of [servo_id, pulse_width] pairs
```

## Architecture Summary

```
┌─────────────────────────┐
│   Raspberry Pi 5        │
│   (Main Controller)      │
│   - Python SDK           │
│   - OpenCV               │
│   - Camera processing    │
└───────────┬──────────────┘
            │ USB/Serial
            │ 1 Mbps
┌───────────▼──────────────┐
│   STM32 Control Board    │  ← Expansion/Control Board
│   (Hardware Interface)    │
│   - Servo controllers     │
│   - Motor drivers         │
│   - IMU sensor            │
│   - GPIO/I2C peripherals  │
└───────────┬──────────────┘
            │
┌───────────▼──────────────┐
│   Hardware Components    │
│   - 18 Bus Servos         │
│   - 4 PWM Servos (head)  │
│   - 4 Motors              │
│   - IMU                   │
│   - Camera                │
│   - LEDs, Buzzer, etc.    │
└───────────────────────────┘
```

## Additional Hardware Features

### Camera System
- **Type:** High-definition USB camera
- **DOF:** 2 degrees of freedom (pan and tilt)
- **Integration:** OpenCV for image processing
- **Capabilities:**
  - Color recognition
  - Object tracking
  - Face recognition
  - Line following
  - AprilTag detection

### Sensors Available
- **Touch Sensor:** Capacitive sensing (GPIO21/GPIO22)
- **Dot Matrix Display:** LED matrix control
- **Sonar:** Ultrasonic distance sensor
- **Color Sensor:** RGB color detection
- **Additional GPIO:** For custom sensors

### AI Capabilities
- **MediaPipe Integration:** Motion control
- **AI Voice Module (WonderEcho Pro):** Voice interaction
  - Wake word: "Hello, HiWonder" (can be changed to "TonyPi")
  - Multimodal model integration
- **Embodied AI:** Environment understanding and task planning

### Communication Interfaces
- **Serial:** `/dev/ttyAMA0` at 1 Mbps (STM32 board)
- **USB:** Multiple USB ports for peripherals
- **GPIO:** Raspberry Pi GPIO for sensors
- **I2C/SPI:** For additional sensors/modules
- **WiFi:** For mobile app connection
- **Bluetooth:** (if enabled on Raspberry Pi)

## Key Findings for Custom Development

### ✅ Advantages
1. **Protocol is Documented in Code**
   - All packet formats visible in SDK
   - Function codes, data formats, checksums all clear
   - Can be reverse-engineered completely

2. **Standard Interfaces**
   - Serial port is standard Linux
   - No special drivers needed
   - Works on Ubuntu/Raspbian

3. **Open Source SDK**
   - Python code is available
   - Can see exactly how everything works
   - Can build custom implementations

### ⚠️ Limitations
1. **Poor Official Documentation**
   - Hardware specs not well documented
   - Protocol documentation is minimal
   - Must rely on code inspection

2. **Vendor-Specific**
   - Custom protocol (not standard)
   - Tied to Hiwonder hardware
   - Limited community support

3. **No Standard ROS Integration**
   - Not standard ROS framework
   - Would need custom ROS nodes if desired

## Recommendations for Custom Control

Based on this analysis:

1. **Use SDK Initially**
   - Protocol is complex but documented in code
   - All functionality is available
   - Faster development

2. **Document as You Go**
   - Create your own documentation
   - Build wrapper classes with clean APIs
   - Your documentation will be better than vendor's

3. **Custom Implementation Possible**
   - Protocol can be fully reimplemented
   - Estimate: 2-4 weeks for complete implementation
   - All information is in the SDK code

4. **ROS Integration**
   - Can build custom ROS nodes
   - Protocol is fully understood from SDK
   - Standard serial communication works everywhere

## Useful Resources

- **Official Docs:** https://docs.hiwonder.com/projects/TonyPi_Pro/
- **SDK Code:** `/home/pi/TonyPi/HiwonderSDK/`
- **Protocol Definition:** `HiwonderSDK/hiwonder/ros_robot_controller_sdk.py`
- **Example Code:** Various examples in `/home/pi/TonyPi/Functions/`

---

**Note:** Most detailed hardware specifications are not publicly documented. The information above is compiled from:
1. SDK source code analysis
2. Official Hiwonder documentation (general info)
3. Code examples and tutorials
4. Reverse engineering of the protocol from SDK

For specific hardware specs, you may need to contact Hiwonder support or inspect the physical board.

