# Board Abstraction Analysis

## Is This Standard ROS SDK?

**No, this is NOT a standard ROS (Robot Operating System) SDK.**

Despite the filename `ros_robot_controller_sdk.py`, this is:
- **Custom STM32-based SDK** - The file header states `# stm32 python sdk`
- **Direct Serial Communication** - Uses pySerial to communicate with hardware via `/dev/ttyAMA0`
- **Not ROS Framework** - No rospy, roscpp, or ROS nodes/topics/services

The "ros" in the filename appears to be misleading or stands for something else (possibly "Robot Operating System" in a generic sense, but not the actual ROS framework).

---

## How Board is Abstracted

### 1. **Hardware Communication Layer**

The `Board` class abstracts the low-level serial communication with the STM32 microcontroller board:

```python
class Board:
    def __init__(self, device="/dev/ttyAMA0", baudrate=1000000, timeout=5):
        # Opens serial port to hardware
        self.port = serial.Serial(None, baudrate, timeout=timeout)
        self.port.setPort(device)
        self.port.open()
```

**Abstraction:** Direct hardware → Serial port → Python object

### 2. **Protocol Layer**

The Board implements a **custom binary packet protocol**:

```
Packet Format: 0xAA 0x55 [Length] [Function] [ID] [Data...] [Checksum]
```

**Packet Types (PacketFunction enum):**
- `PACKET_FUNC_SYS` - System functions
- `PACKET_FUNC_LED` - LED control
- `PACKET_FUNC_BUZZER` - Buzzer control
- `PACKET_FUNC_MOTOR` - Motor control
- `PACKET_FUNC_PWM_SERVO` - PWM servo control
- `PACKET_FUNC_BUS_SERVO` - Bus servo control
- `PACKET_FUNC_KEY` - Button/key reading
- `PACKET_FUNC_IMU` - IMU sensor reading
- `PACKET_FUNC_GAMEPAD` - Gamepad input
- `PACKET_FUNC_SBUS` - SBus receiver
- `PACKET_FUNC_OLED` - OLED display
- `PACKET_FUNC_RGB` - RGB LED control

**Abstraction:** Raw bytes → Structured packets → Function calls

### 3. **Asynchronous Data Reception**

The Board uses threading to handle incoming data asynchronously:

```python
def __init__(self, ...):
    # Queues for different data types
    self.sys_queue = queue.Queue(maxsize=1)
    self.bus_servo_queue = queue.Queue(maxsize=1)
    self.pwm_servo_queue = queue.Queue(maxsize=1)
    self.key_queue = queue.Queue(maxsize=1)
    self.imu_queue = queue.Queue(maxsize=1)
    self.gamepad_queue = queue.Queue(maxsize=1)
    self.sbus_queue = queue.Queue(maxsize=1)
    
    # Packet parsers for each function type
    self.parsers = {
        PacketFunction.PACKET_FUNC_SYS: self.packet_report_sys,
        PacketFunction.PACKET_FUNC_IMU: self.packet_report_imu,
        # ... etc
    }
    
    # Start background thread for receiving data
    threading.Thread(target=self.recv_task, daemon=True).start()
```

**Abstraction:** Blocking I/O → Non-blocking queues → Event-driven reading

### 4. **High-Level API Methods**

The Board provides high-level methods that hide protocol details:

```python
# Servo control
board.bus_servo_set_position(duration, positions)
board.bus_servo_read_position(servo_id)

# Sensor reading
board.get_imu()  # Returns (ax, ay, az, gx, gy, gz)

# Motor control
board.set_motor_speed([[motor_id, speed], ...])

# Buzzer/LED control
board.set_buzzer(freq, on_time, off_time, repeat)
board.set_led(on_time, off_time, repeat)
```

**Abstraction:** Protocol packets → Simple function calls

---

## Architecture Layers

```
┌─────────────────────────────────────┐
│  User Code (Controller class)       │  ← High-level API
│  ctl.set_bus_servo_pulse(id, pos)   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Controller Class (Wrapper)         │  ← Retry logic, timeout handling
│  - Adds timeout/retry logic         │
│  - Validates data                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Board Class (Protocol Layer)        │  ← Packet construction/parsing
│  - Serial communication              │
│  - Packet protocol                   │
│  - Threading/queues                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Serial Port (/dev/ttyAMA0)          │  ← Hardware I/O
│  - 1,000,000 baud                    │
│  - Binary protocol                   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  STM32 Control Board                 │  ← Hardware
│  - Servo controllers                 │
│  - IMU sensor                        │
│  - Motor drivers                      │
│  - GPIO pins                          │
└─────────────────────────────────────┘
```

---

## Key Abstraction Patterns Used

### 1. **Facade Pattern**
The `Board` class provides a simple interface that hides the complexity of:
- Serial communication
- Packet encoding/decoding
- Checksum calculation
- Thread management
- Queue management

### 2. **Producer-Consumer Pattern**
- **Producer:** Background thread (`recv_task`) receives data and puts it in queues
- **Consumer:** User code reads from queues via `get_imu()`, `get_battery()`, etc.

### 3. **Protocol Encapsulation**
Raw serial bytes are encapsulated into structured packets with:
- Function codes (what operation to perform)
- Data payload (parameters)
- Checksums (error detection)

### 4. **Dependency Injection**
The `Controller` class accepts a `Board` instance in its constructor:

```python
class Controller:
    def __init__(self, board, time_out=50):
        self.board = board  # Board instance injected
```

This allows:
- Testing with mock boards
- Multiple controllers using different boards
- Board swapping without changing Controller code

**Note:** However, there's also a global `board = rrc.Board()` at module level (line 4) which is odd - it creates an unused global instance.

---

## What Board Abstracts From

1. **Serial Port Details**
   - Baud rate (1Mbps)
   - Device path (`/dev/ttyAMA0`)
   - Flow control (RTS/DTR)
   - Timeout handling

2. **Protocol Details**
   - Packet framing (0xAA 0x55 headers)
   - Checksum calculation (CRC8)
   - Function codes
   - Data encoding/decoding

3. **Hardware Details**
   - Servo communication (bus vs PWM)
   - Sensor reading (IMU, buttons)
   - Motor control
   - Peripheral control (LEDs, buzzer, OLED)

4. **Concurrency Details**
   - Thread management
   - Queue synchronization
   - Lock management (for servo reads)

---

## Example: Tracing a Call

When you call `ctl.set_bus_servo_pulse(1, 250, 500)`:

1. **Controller.set_bus_servo_pulse()** (line 178-179)
   - Converts `use_time` from ms to seconds
   - Calls `self.board.bus_servo_set_position()`

2. **Board.bus_servo_set_position()** (line 421-426)
   - Converts duration to milliseconds
   - Constructs packet: `[0x01, duration_low, duration_high, count, [servo_id, pulse], ...]`
   - Calls `self.buf_write(PacketFunction.PACKET_FUNC_BUS_SERVO, data)`

3. **Board.buf_write()** (line 314-319)
   - Creates packet: `[0xAA, 0x55, function, length, data..., checksum]`
   - Calculates CRC8 checksum
   - Writes to serial port: `self.port.write(buf)`

4. **Serial Port → Hardware**
   - Bytes transmitted to `/dev/ttyAMA0`
   - STM32 board receives and processes packet
   - Servo moves to position 250 over 500ms

---

## Summary

The `Board` class is a **hardware abstraction layer** that:
- ✅ Abstracts serial communication and protocol details
- ✅ Provides high-level API for robot control
- ✅ Handles concurrency with threading and queues
- ✅ Encapsulates STM32-specific communication
- ❌ NOT a ROS SDK (despite filename)
- ⚠️ Has odd global instance creation in Controller.py

This is a **custom, proprietary SDK** for Hiwonder's STM32-based robot control board.

