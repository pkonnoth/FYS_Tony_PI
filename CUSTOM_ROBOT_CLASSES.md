# Custom Robot Classes Design Strategy

## Should You Use Action Groups or Direct Servo Control?

### Recommendation: **Hybrid Approach** ⭐

Use **both** action groups and direct servo control, depending on the use case:

1. **Action Groups** → High-level behaviors (walking, standing, gestures)
2. **Direct Servo Control** → Fine-grained control (custom poses, precise movements)

## Why Hybrid?

### Action Groups - When to Use ✅

**Best for:**
- ✅ Complex, tested movements (walking, turning, climbing stairs)
- ✅ Quick prototyping
- ✅ High-level AI commands ("walk forward", "stand up")
- ✅ Pre-programmed routines (dance, exercises)
- ✅ Movements that require precise timing coordination

**Example:**
```python
robot.walk_forward(5)  # Uses action group - complex, tested
robot.stand()          # Uses action group - reliable
robot.wave()           # Uses action group - pre-programmed gesture
```

### Direct Servo Control - When to Use ✅

**Best for:**
- ✅ Custom poses and positions
- ✅ Precise joint control
- ✅ Custom movement sequences
- ✅ Fine-tuning and calibration
- ✅ Individual limb control
- ✅ Real-time adjustments

**Example:**
```python
robot.left_leg.set_pose(hip=250, knee=300, ankle=200)  # Direct control
robot.head.look_at(pan=1200, tilt=1800)  # Direct control for precise aiming
```

## Recommended Class Structure

```python
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC
import time

class RobotServo:
    """Individual servo abstraction with direct control"""
    def __init__(self, controller, servo_id, min_pos=0, max_pos=500):
        self.controller = controller
        self.id = servo_id
        self.min_pos = min_pos
        self.max_pos = max_pos
    
    def move_to(self, position, duration_ms=500):
        """Move servo to position directly"""
        position = max(self.min_pos, min(self.max_pos, position))  # Clamp
        self.controller.set_bus_servo_pulse(self.id, position, duration_ms)
    
    def get_position(self):
        """Get current servo position"""
        return self.controller.get_bus_servo_pulse(self.id)
    
    def get_temperature(self):
        """Get servo temperature"""
        return self.controller.get_bus_servo_temp(self.id)

class RobotLimb:
    """Represents a limb (leg or arm) with multiple servos"""
    def __init__(self, controller, servo_ids, servo_names):
        self.controller = controller
        self.servos = {}
        for name, servo_id in zip(servo_names, servo_ids):
            self.servos[name] = RobotServo(controller, servo_id)
    
    def set_pose(self, **kwargs):
        """Set all servos in limb to specified positions"""
        # kwargs: {'hip': 250, 'knee': 300, 'ankle': 200}
        for name, position in kwargs.items():
            if name in self.servos:
                self.servos[name].move_to(position)

class RobotHead:
    """Head control - uses PWM servos"""
    def __init__(self, controller):
        self.controller = controller
        self.pan_servo_id = 1   # Head pan (left-right)
        self.tilt_servo_id = 2  # Head tilt (up-down)
    
    def look_at(self, pan=1500, tilt=1500, duration_ms=300):
        """Look at specific pan/tilt position (PWM servos)"""
        self.controller.set_pwm_servo_pulse(self.pan_servo_id, pan, duration_ms)
        self.controller.set_pwm_servo_pulse(self.tilt_servo_id, tilt, duration_ms)
    
    def center(self):
        """Center the head"""
        self.look_at(pan=1500, tilt=1500)
    
    def look_left(self):
        """Look left"""
        self.look_at(pan=1200)
    
    def look_right(self):
        """Look right"""
        self.look_at(pan=1800)

class TonyPiRobot:
    """
    Main robot class - HYBRID approach
    
    Uses:
    - Action groups for complex, tested movements
    - Direct servo control for fine-grained control
    """
    
    def __init__(self):
        """Initialize robot with all components"""
        # Initialize SDK
        self.board = rrc.Board()
        self.controller = Controller(self.board)
        self.controller.enable_recv()
        
        # Initialize components
        self.head = RobotHead(self.controller)
        
        # Define servo IDs (adjust based on your robot's configuration)
        # Left leg servos
        self.left_leg = RobotLimb(
            self.controller,
            servo_ids=[1, 2, 3],  # Adjust to your robot
            servo_names=['hip', 'knee', 'ankle']
        )
        
        # Right leg servos
        self.right_leg = RobotLimb(
            self.controller,
            servo_ids=[4, 5, 6],  # Adjust to your robot
            servo_names=['hip', 'knee', 'ankle']
        )
        
        # Left arm servos
        self.left_arm = RobotLimb(
            self.controller,
            servo_ids=[7, 8, 9],  # Adjust to your robot
            servo_names=['shoulder', 'elbow', 'wrist']
        )
        
        # Right arm servos
        self.right_arm = RobotLimb(
            self.controller,
            servo_ids=[10, 11, 12],  # Adjust to your robot
            servo_names=['shoulder', 'elbow', 'wrist']
        )
        
        # Find action groups path
        self.action_groups_path = self._find_action_groups_path()
        
        print(f"Robot initialized. Action groups path: {self.action_groups_path}")
    
    def _find_action_groups_path(self):
        """Find where action group files are located"""
        import os
        possible_paths = [
            '/home/pi/TonyPi/ActionGroups/',
            '/home/pi/one/tonypi_pro/TonyPi/ActionGroups/',
            '/home/pi/tonypi_pro/TonyPi/ActionGroups/',
        ]
        for path in possible_paths:
            test_file = os.path.join(path, 'go_forward.d6a')
            if os.path.exists(test_file):
                return path
        return '/home/pi/TonyPi/ActionGroups/'
    
    # ==========================================
    # HIGH-LEVEL MOVEMENTS (Action Groups)
    # ==========================================
    
    def stand(self):
        """Stand using action group - reliable, tested movement"""
        AGC.runActionGroup('stand_slow', times=1, path=self.action_groups_path)
    
    def walk_forward(self, steps=1, speed='normal'):
        """Walk forward using action group"""
        if speed == 'slow':
            action = 'go_forward_slow'
        elif speed == 'fast':
            action = 'go_forward_fast'
        else:
            action = 'go_forward'
        AGC.runActionGroup(action, times=steps, with_stand=True, 
                          path=self.action_groups_path)
    
    def walk_backward(self, steps=1):
        """Walk backward using action group"""
        AGC.runActionGroup('back', times=steps, with_stand=True,
                          path=self.action_groups_path)
    
    def turn_left(self, times=1):
        """Turn left using action group"""
        AGC.runActionGroup('turn_left', times=times, path=self.action_groups_path)
    
    def turn_right(self, times=1):
        """Turn right using action group"""
        AGC.runActionGroup('turn_right', times=times, path=self.action_groups_path)
    
    def wave(self, times=3):
        """Wave hand using action group"""
        AGC.runActionGroup('wave', times=times, path=self.action_groups_path)
    
    def bow(self):
        """Bow using action group"""
        AGC.runActionGroup('bow', times=1, path=self.action_groups_path)
    
    def get_up_from_front(self):
        """Stand up from front fall"""
        AGC.runActionGroup('stand_up_front', times=1, path=self.action_groups_path)
    
    def get_up_from_back(self):
        """Stand up from back fall"""
        AGC.runActionGroup('stand_up_back', times=1, path=self.action_groups_path)
    
    # ==========================================
    # FINE-GRAINED CONTROL (Direct Servo)
    # ==========================================
    
    def set_left_leg_pose(self, hip=None, knee=None, ankle=None, duration_ms=500):
        """Set left leg pose using direct servo control"""
        self.left_leg.set_pose(hip=hip, knee=knee, ankle=ankle)
        time.sleep(duration_ms / 1000.0)
    
    def set_right_leg_pose(self, hip=None, knee=None, ankle=None, duration_ms=500):
        """Set right leg pose using direct servo control"""
        self.right_leg.set_pose(hip=hip, knee=knee, ankle=ankle)
        time.sleep(duration_ms / 1000.0)
    
    def set_pose(self, left_leg=None, right_leg=None, left_arm=None, 
                 right_arm=None, head=None, duration_ms=500):
        """
        Set full robot pose using direct servo control
        
        Args:
            left_leg: dict with {'hip': pos, 'knee': pos, 'ankle': pos}
            right_leg: dict with {'hip': pos, 'knee': pos, 'ankle': pos}
            left_arm: dict with {'shoulder': pos, 'elbow': pos, 'wrist': pos}
            right_arm: dict with {'shoulder': pos, 'elbow': pos, 'wrist': pos}
            head: dict with {'pan': pos, 'tilt': pos}
        """
        if left_leg:
            self.left_leg.set_pose(**left_leg)
        if right_leg:
            self.right_leg.set_pose(**right_leg)
        if left_arm:
            self.left_arm.set_pose(**left_arm)
        if right_arm:
            self.right_arm.set_pose(**right_arm)
        if head:
            self.head.look_at(**head)
        
        time.sleep(duration_ms / 1000.0)
    
    # ==========================================
    # SENSORS & STATUS
    # ==========================================
    
    def get_imu(self):
        """Get IMU sensor data"""
        return self.controller.get_imu()
    
    def get_battery_voltage(self):
        """Get battery voltage"""
        return self.board.get_battery()
    
    def get_servo_temperature(self, servo_id):
        """Get servo temperature"""
        return self.controller.get_bus_servo_temp(servo_id)
    
    # ==========================================
    # COMPOSITE BEHAVIORS (Mixing both)
    # ==========================================
    
    def dance(self):
        """Dance routine - mix of action groups and direct control"""
        # Start with action group
        self.wave(times=2)
        time.sleep(0.5)
        
        # Add custom pose
        self.set_pose(
            left_arm={'shoulder': 200, 'elbow': 300},
            right_arm={'shoulder': 300, 'elbow': 200}
        )
        time.sleep(1)
        
        # Continue with action group
        AGC.runActionGroup('twist', times=3, path=self.action_groups_path)
        time.sleep(0.5)
        
        # End with action group
        self.bow()
    
    def navigate_square(self, steps_per_side=2):
        """Navigate in a square pattern"""
        for _ in range(4):
            self.walk_forward(steps=steps_per_side)
            time.sleep(0.5)
            self.turn_right(times=1)
            time.sleep(0.5)
    
    # ==========================================
    # SAFETY & UTILITIES
    # ==========================================
    
    def stop_all_movements(self):
        """Stop all current movements"""
        AGC.stopActionGroup()
    
    def safe_position(self):
        """Move to safe, stable position"""
        self.stand()
        self.head.center()
    
    def check_servo_health(self):
        """Check all servo temperatures"""
        health = {}
        for servo_id in range(1, 17):  # Check servos 1-16
            temp = self.get_servo_temperature(servo_id)
            if temp is not None:
                health[servo_id] = {
                    'temperature': temp,
                    'status': 'OK' if temp < 70 else 'WARNING'
                }
        return health

# ==========================================
# USAGE EXAMPLES
# ==========================================

if __name__ == '__main__':
    # Initialize robot
    robot = TonyPiRobot()
    
    # Example 1: Use action groups for reliable movements
    robot.stand()
    time.sleep(2)
    robot.walk_forward(steps=5, speed='normal')
    robot.turn_right(times=1)
    robot.walk_forward(steps=3)
    
    # Example 2: Use direct control for custom poses
    robot.set_pose(
        left_leg={'hip': 250, 'knee': 300, 'ankle': 200},
        right_leg={'hip': 250, 'knee': 300, 'ankle': 200}
    )
    
    # Example 3: Mix both
    robot.dance()
    
    # Example 4: Sensor monitoring
    imu_data = robot.get_imu()
    if imu_data:
        print(f"IMU: {imu_data}")
    
    # Cleanup
    robot.safe_position()

