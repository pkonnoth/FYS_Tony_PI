# Custom Control Architecture Decision Guide

## Current Situation Analysis

### What You Have Now

**Hardware:**
- Hiwonder TonyPi robot with STM32 control board
- Raspberry Pi running the control software
- Serial communication: `/dev/ttyAMA0` at 1,000,000 baud
- Custom binary protocol (documented in code)

**Software:**
- Hiwonder SDK (`ros_robot_controller_sdk.py`) - **NOT actual ROS**
- Proprietary SDK with poor documentation
- Python-based serial communication layer

### The STM32 Board Protocol

The board uses a **well-defined binary protocol** that is **fully reverse-engineerable** from the SDK code:

```
Packet Format: [0xAA 0x55] [Function] [Length] [Data...] [CRC8]
```

All function codes, data formats, and checksum algorithms are visible in the SDK.

---

## Option 1: Build on Hiwonder SDK (Recommended for Quick Start)

### Pros ✅

1. **Immediate Functionality**
   - All hardware functions already working
   - Servo control, IMU, sensors, motors, LEDs, etc. all functional
   - No need to reverse engineer protocol

2. **Time to Market**
   - Can start building your custom classes immediately
   - No low-level protocol work needed
   - Faster development cycle

3. **Proven Stability**
   - SDK is already tested and working
   - Less risk of hardware compatibility issues

4. **MCP Integration**
   - Can wrap SDK calls in clean Python classes
   - Easy to expose functions via MCP protocol
   - No additional abstraction needed

5. **Documentation You Control**
   - You can document YOUR wrapper classes
   - Create clean API that makes sense for your use case
   - Better than fighting with vendor docs

### Cons ❌

1. **Vendor Lock-in**
   - Dependent on Hiwonder's SDK updates
   - Less flexibility if they change things

2. **Limited Understanding**
   - Don't fully understand the protocol (though it's reverse-engineerable)
   - May hit limitations in SDK

3. **Poor Documentation**
   - As you mentioned, vendor docs are poor
   - Must rely on code inspection

### Implementation Approach

```python
# Custom wrapper classes over Hiwonder SDK
class RobotServo:
    def __init__(self, controller, servo_id):
        self.controller = controller
        self.id = servo_id
    
    def move_to(self, position, duration_ms):
        self.controller.set_bus_servo_pulse(self.id, position, duration_ms)
    
    def get_position(self):
        return self.controller.get_bus_servo_pulse(self.id)

class RobotLeg:
    def __init__(self, controller, servo_ids):
        self.hip = RobotServo(controller, servo_ids[0])
        self.knee = RobotServo(controller, servo_ids[1])
        self.ankle = RobotServo(controller, servo_ids[2])
    
    def walk_forward(self):
        # Your custom walking logic
        pass

class TonyPiRobot:
    def __init__(self):
        self.board = rrc.Board()
        self.controller = Controller(self.board)
        # ... initialize legs, arms, head, etc.
    
    def stand(self):
        # Your custom standing logic
        pass
```

---

## Option 2: Custom ROS Implementation (More Control, More Work)

### Pros ✅

1. **Full Control**
   - Understand every aspect of communication
   - Can optimize protocol handling
   - No vendor dependencies

2. **Better Documentation**
   - ROS has excellent documentation
   - Standard patterns and best practices
   - Large community

3. **Modularity**
   - Standard ROS node architecture
   - Easy to add new sensors/actuators
   - Standard message types

4. **Integration**
   - Easy to integrate with other ROS tools (RViz, Gazebo)
   - Can use standard ROS packages (navigation, manipulation, etc.)
   - Industry standard

5. **Future Proofing**
   - If you switch hardware, ROS nodes can be adapted
   - Standard interface patterns

### Cons ❌

1. **Significant Development Time**
   - Must reverse engineer protocol from SDK
   - Write serial communication layer
   - Write protocol encoder/decoder
   - Test all hardware functions
   - **Estimated: 2-4 weeks of work**

2. **Risk**
   - May miss edge cases in protocol
   - Hardware compatibility issues
   - Need to test thoroughly

3. **Ubuntu Setup Complexity**
   - Must flash/reconfigure Raspberry Pi
   - ROS installation and setup
   - May break existing system
   - Need to ensure hardware drivers work

4. **MCP Integration**
   - Need ROS-to-MCP bridge layer
   - Additional abstraction complexity

### Implementation Approach

```python
# ROS node structure
import rospy
from std_msgs.msg import Float64, Int32
from sensor_msgs.msg import Imu

class STM32BoardDriver:
    def __init__(self):
        self.port = serial.Serial("/dev/ttyAMA0", 1000000)
        # Your protocol implementation
        
    def send_packet(self, function, data):
        # Build packet: 0xAA 0x55 [func] [len] [data] [crc8]
        pass
    
    def receive_packet(self):
        # Parse incoming packets
        pass

class ServoControllerNode(rospy.Node):
    def __init__(self):
        super().__init__("servo_controller")
        self.board = STM32BoardDriver()
        self.pub = rospy.Publisher("/servo_position", Int32)
        self.sub = rospy.Subscriber("/servo_command", Float64, self.callback)
    
    def callback(self, msg):
        # Handle servo command
        pass
```

---

## Option 3: Hybrid Approach (Best of Both Worlds) ⭐ RECOMMENDED

### Strategy

1. **Short Term: Build Clean Wrapper Over SDK**
   - Create your custom classes using Hiwonder SDK
   - Document everything yourself
   - Get MCP integration working quickly

2. **Long Term: Gradual Migration to Custom**
   - As you use features, implement custom versions
   - Replace SDK calls one module at a time
   - Eventually have full control

3. **Protocol Documentation**
   - Reverse engineer and document the protocol as you go
   - Create your own protocol library
   - Keep it compatible with SDK

### Benefits

- ✅ Fast initial development
- ✅ Progressive improvement
- ✅ Lower risk
- ✅ Best documentation (yours!)
- ✅ Eventually full control

---

## Can You Control Servo Board with Custom ROS Setup?

### YES, Absolutely! ✅

The protocol is **fully documented in the SDK code**:

1. **Protocol is Reverse-Engineerable**
   ```python
   # From ros_robot_controller_sdk.py, line 314-319
   def buf_write(self, func, data):
       buf = [0xAA, 0x55, int(func)]
       buf.append(len(data))
       buf.extend(data)
       buf.append(checksum_crc8(bytes(buf[2:])))
       self.port.write(buf)
   ```

2. **All Function Codes Documented**
   - `PACKET_FUNC_BUS_SERVO = 5`
   - `PACKET_FUNC_PWM_SERVO = 4`
   - `PACKET_FUNC_IMU = 7`
   - etc. (all in SDK)

3. **Serial Interface is Standard**
   - Just `/dev/ttyAMA0` at 1Mbps
   - Standard pySerial works
   - No special drivers needed

4. **Checksum Algorithm Visible**
   - CRC8 table is in SDK (line 50-67)
   - Checksum function visible (line 69-74)

### What You'd Need to Implement

1. **Packet Builder** - Easy (copy from SDK)
2. **Packet Parser** - Medium (state machine from SDK)
3. **Function Wrappers** - Medium (translate ROS messages to packets)
4. **Threading/Queues** - Medium (SDK shows pattern)

**Estimated effort: 2-4 weeks** for complete implementation and testing.

---

## Recommendation for Your Use Case

Given your goals:
- Custom control code ✅
- Clean classes representing robot ✅
- AI access via MCP protocol ✅
- Better control than SDK ✅
- Better documentation ✅

### I Recommend: **Option 3 - Hybrid Approach**

**Phase 1 (Week 1-2):**
```python
# Build clean wrapper classes over SDK
class TonyPiRobot:
    """Main robot class with clean API"""
    def __init__(self):
        self.board = rrc.Board()
        self.controller = Controller(self.board)
        self.controller.enable_recv()
        
        # Initialize robot parts
        self.head = Head(self.controller)
        self.left_leg = Leg(self.controller, [1, 2, 3])
        self.right_leg = Leg(self.controller, [4, 5, 6])
        # ... etc
    
    def stand(self):
        """Clean, documented method"""
        # Your implementation
        pass
    
    def walk(self, steps, speed):
        """Clean, documented method"""
        # Your implementation
        pass
```

**Phase 2 (Week 3-4):**
- Expose via MCP protocol
- Document everything
- Test thoroughly

**Phase 3 (Month 2-3):**
- If you hit SDK limitations, implement custom protocol layer
- Gradually replace SDK calls
- Keep same API (users don't notice)

---

## ROS Setup Feasibility

### Can You Flash Ubuntu and Setup ROS?

**YES, but consider:**

1. **Current OS**
   - What OS are you running now? (likely Raspbian/Raspberry Pi OS)
   - Ubuntu support for Raspberry Pi is available

2. **Hardware Compatibility**
   - `/dev/ttyAMA0` works on Ubuntu
   - Serial drivers are standard Linux
   - No special hardware drivers needed

3. **Migration Path**
   ```
   Current Setup → Backup → Flash Ubuntu → Install ROS → 
   Implement Protocol → Test → Deploy
   ```

4. **Risk Assessment**
   - Medium risk: May break existing setup
   - Need backup/recovery plan
   - Time investment significant

---

## Quick Decision Matrix

| Factor | Hiwonder SDK | Custom ROS | Hybrid |
|--------|--------------|------------|--------|
| **Time to Working** | 1 week | 4 weeks | 1 week |
| **Control Level** | Medium | High | High (eventually) |
| **Documentation** | Poor | Good | Excellent (yours) |
| **MCP Integration** | Easy | Medium | Easy |
| **Risk** | Low | Medium | Low |
| **Future Flexibility** | Limited | High | High |
| **Maintenance** | Vendor dependent | You control | You control |

---

## Specific Recommendation for MCP + AI Access

### Use Wrapper Approach Initially

**Why:**
1. **MCP Integration is Language-Agnostic**
   - MCP works with Python functions
   - Doesn't care if you call SDK or custom ROS
   - Your wrapper classes = clean MCP interface

2. **AI Needs Clean API**
   - AI doesn't need to know about protocol details
   - Your wrapper provides semantic operations:
     - `robot.walk_forward(5)` ✅
     - `robot.set_servo_register(0x05, 250)` ❌

3. **You Can Switch Later**
   - MCP interface stays the same
   - Replace SDK with ROS implementation
   - AI code doesn't change

### Example MCP Integration

```python
# Your clean robot class
class TonyPiRobot:
    def walk_forward(self, steps: int = 1) -> bool:
        """Walk robot forward specified number of steps"""
        # Uses SDK internally
        pass
    
    def get_imu_data(self) -> dict:
        """Get IMU sensor data"""
        # Returns clean dict, not raw protocol
        return {"ax": ..., "ay": ..., "az": ...}

# MCP server exposes these methods
# AI calls: robot.walk_forward(5)
# No knowledge of SDK or protocol needed!
```

---

## Conclusion

**My Strong Recommendation:**

1. **Start with SDK wrapper** (1-2 weeks)
   - Build clean classes representing robot
   - Document everything yourself
   - Expose via MCP
   - Get AI access working quickly

2. **Evaluate after 1-2 months**
   - If SDK works well → stick with it
   - If you hit limitations → implement custom layer
   - You'll have full protocol understanding by then

3. **Consider ROS later if:**
   - You need ROS ecosystem tools
   - You want to integrate other ROS components
   - SDK becomes a blocker
   - You have 2-4 weeks for implementation

**This gives you:**
- ✅ Fast development
- ✅ Clean, documented API
- ✅ MCP integration
- ✅ Future flexibility
- ✅ Lower risk

Would you like me to start building the wrapper classes?

