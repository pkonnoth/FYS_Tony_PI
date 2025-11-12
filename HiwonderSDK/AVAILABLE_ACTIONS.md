# Available Preprogrammed Actions

The Hiwonder robot comes with many preprogrammed action groups that you can use directly in your code. These are stored in `/home/pi/TonyPi/ActionGroups/` as `.d6a` files.

## Quick Start

```python
import hiwonder.ActionGroupControl as AGC

# Run a single action once
AGC.runActionGroup('go_forward', times=1)

# Run an action multiple times
AGC.runActionGroup('wave', times=5)

# Run with stand at end
AGC.runActionGroup('go_forward', times=3, with_stand=True)
```

---

## Complete List of Available Actions

### Basic Movement Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'go_forward'` | Walk forward | `AGC.runActionGroup('go_forward', times=5)` |
| `'go_forward_slow'` | Walk forward slowly | `AGC.runActionGroup('go_forward_slow', times=3)` |
| `'go_forward_fast'` | Walk forward quickly | `AGC.runActionGroup('go_forward_fast', times=3)` |
| `'back'` | Walk backward | `AGC.runActionGroup('back', times=3)` |
| `'back_fast'` | Walk backward quickly | `AGC.runActionGroup('back_fast', times=2)` |
| `'turn_left'` | Turn left | `AGC.runActionGroup('turn_left', times=1)` |
| `'turn_right'` | Turn right | `AGC.runActionGroup('turn_right', times=1)` |
| `'left_move'` | Move left | `AGC.runActionGroup('left_move', times=2)` |
| `'left_move_fast'` | Move left quickly | `AGC.runActionGroup('left_move_fast', times=2)` |
| `'right_move'` | Move right | `AGC.runActionGroup('right_move', times=2)` |
| `'right_move_fast'` | Move right quickly | `AGC.runActionGroup('right_move_fast', times=2)` |
| `'left_move_large'` | Large movement left | `AGC.runActionGroup('left_move_large', times=1)` |
| `'right_move_large'` | Large movement right | `AGC.runActionGroup('right_move_large', times=1)` |
| `'go_forward_one_step'` | Take one step forward | `AGC.runActionGroup('go_forward_one_step')` |
| `'go_forward_one_small_step'` | Take one small step forward | `AGC.runActionGroup('go_forward_one_small_step')` |

### Standing and Posture Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'stand'` | Stand at attention | `AGC.runActionGroup('stand', times=1)` |
| `'stand_slow'` | Stand slowly | `AGC.runActionGroup('stand_slow', times=1)` |
| `'stepping'` | March in place | `AGC.runActionGroup('stepping', times=10)` |

### Gesture and Expression Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'wave'` | Wave hand | `AGC.runActionGroup('wave', times=3)` |
| `'bow'` | Bow | `AGC.runActionGroup('bow', times=1)` |
| `'jugong'` | Bow (alternate) | `AGC.runActionGroup('jugong', times=1)` |
| `'chest'` | Celebration pose | `AGC.runActionGroup('chest', times=1)` |
| `'twist'` | Twist waist | `AGC.runActionGroup('twist', times=5)` |

### Exercise Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'push_ups'` | Push-ups | `AGC.runActionGroup('push_ups', times=3)` |
| `'sit_ups'` | Sit-ups | `AGC.runActionGroup('sit_ups', times=3)` |
| `'squat'` | Squat | `AGC.runActionGroup('squat', times=5)` |
| `'weightlifting'` | Weightlifting | `AGC.runActionGroup('weightlifting', times=1)` |

### Martial Arts Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'wing_chun'` | Wing Chun moves | `AGC.runActionGroup('wing_chun', times=1)` |
| `'left_kick'` | Left kick | `AGC.runActionGroup('left_kick', times=1)` |
| `'right_kick'` | Right kick | `AGC.runActionGroup('right_kick', times=1)` |
| `'left_shot_fast'` | Left foot kick (fast) | `AGC.runActionGroup('left_shot_fast', times=1)` |
| `'right_shot_fast'` | Right foot kick (fast) | `AGC.runActionGroup('right_shot_fast', times=1)` |
| `'left_uppercut'` | Left hook punch | `AGC.runActionGroup('left_uppercut', times=1)` |
| `'right_uppercut'` | Right hook punch | `AGC.runActionGroup('right_uppercut', times=1)` |

### Recovery Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'stand_up_front'` | Stand up from front fall | `AGC.runActionGroup('stand_up_front', times=1)` |
| `'stand_up_back'` | Stand up from back fall | `AGC.runActionGroup('stand_up_back', times=1)` |
| `'go_forward_start'` | Start walking forward | `AGC.runActionGroup('go_forward_start')` |
| `'go_forward_end'` | End walking forward | `AGC.runActionGroup('go_forward_end')` |
| `'back_start'` | Start walking backward | `AGC.runActionGroup('back_start')` |
| `'back_end'` | End walking backward | `AGC.runActionGroup('back_end')` |

### Special Course Actions

| Action Name | Description | Example Usage |
|------------|-------------|---------------|
| `'climb_stairs'` | Climb stairs | `AGC.runActionGroup('climb_stairs', times=1)` |
| `'down_floor'` | Go down stairs | `AGC.runActionGroup('down_floor', times=1)` |
| `'hurdles'` | Jump hurdles | `AGC.runActionGroup('hurdles', times=1)` |

---

## Usage Examples

### Example 1: Simple Walking Sequence

```python
import hiwonder.ActionGroupControl as AGC
import time

# Stand first
AGC.runActionGroup('stand_slow', times=1)
time.sleep(1)

# Walk forward 5 steps
AGC.runActionGroup('go_forward', times=5, with_stand=True)

# Turn right
AGC.runActionGroup('turn_right', times=1)
time.sleep(1)

# Walk forward again
AGC.runActionGroup('go_forward', times=3, with_stand=True)
```

### Example 2: Exercise Routine

```python
import hiwonder.ActionGroupControl as AGC
import time

print("Starting exercise routine...")

# Warm up with marching
AGC.runActionGroup('stepping', times=10)
time.sleep(1)

# Do some push-ups
print("Doing push-ups...")
AGC.runActionGroup('push_ups', times=5)
time.sleep(1)

# Do squats
print("Doing squats...")
AGC.runActionGroup('squat', times=5)
time.sleep(1)

# Finish with celebration
AGC.runActionGroup('chest', times=1)
print("Exercise complete!")
```

### Example 3: Continuous Walking with Stop

```python
import hiwonder.ActionGroupControl as AGC
import time
import threading

# Start walking in a thread (non-blocking)
print("Starting continuous walk...")
walk_thread = threading.Thread(
    target=AGC.runActionGroup,
    args=('go_forward', 0, True),  # 0 = infinite loop
    daemon=True
)
walk_thread.start()

# Walk for 10 seconds
time.sleep(10)

# Stop walking
print("Stopping...")
AGC.stopActionGroup()
walk_thread.join()
```

### Example 4: Dance or Performance Routine

```python
import hiwonder.ActionGroupControl as AGC
import time

def dance_routine():
    """Perform a dance routine"""
    # Start pose
    AGC.runActionGroup('stand_slow', times=1)
    time.sleep(0.5)
    
    # Wave
    AGC.runActionGroup('wave', times=3)
    time.sleep(0.5)
    
    # Twist
    AGC.runActionGroup('twist', times=4)
    time.sleep(0.5)
    
    # Move side to side
    AGC.runActionGroup('left_move', times=2)
    time.sleep(0.3)
    AGC.runActionGroup('right_move', times=2)
    time.sleep(0.3)
    
    # Bow
    AGC.runActionGroup('bow', times=1)
    time.sleep(0.5)
    
    # Celebration
    AGC.runActionGroup('chest', times=1)
    time.sleep(1)

dance_routine()
```

### Example 5: Navigation Sequence

```python
import hiwonder.ActionGroupControl as AGC
import time

def navigate_obstacle():
    """Navigate around an obstacle"""
    # Walk forward until obstacle detected
    # (In real code, you'd check sensors here)
    AGC.runActionGroup('go_forward', times=3)
    time.sleep(0.5)
    
    # Turn right
    AGC.runActionGroup('turn_right', times=1)
    time.sleep(0.5)
    
    # Walk past obstacle
    AGC.runActionGroup('go_forward', times=2)
    time.sleep(0.5)
    
    # Turn left
    AGC.runActionGroup('turn_left', times=1)
    time.sleep(0.5)
    
    # Continue forward
    AGC.runActionGroup('go_forward', times=3, with_stand=True)
```

---

## Action Group Function Parameters

### `runActionGroup()` Function

```python
AGC.runActionGroup(actName, times=1, with_stand=False, lock_servos='', path="/home/pi/TonyPi/ActionGroups/")
```

**Parameters:**

1. **`actName`** (str, required)
   - Name of the action group (without `.d6a` extension)
   - Example: `'go_forward'`, `'wave'`, `'stand'`

2. **`times`** (int, default=1)
   - Number of times to repeat the action
   - `1` = run once
   - `5` = run 5 times
   - `0` or `-1` = infinite loop (use with threading)

3. **`with_stand`** (bool, default=False)
   - If `True`, ends with standing action
   - Useful for walking actions to ensure robot ends in stable position

4. **`lock_servos`** (dict or str, default='')
   - Lock specific servos at fixed positions during action
   - Format: `{'1': 250, '3': 300}` (servo_id: position)
   - Example: `lock_servos={'1': 250}` keeps servo 1 at position 250

5. **`path`** (str, default="/home/pi/TonyPi/ActionGroups/")
   - Path to directory containing `.d6a` action files
   - Usually doesn't need to be changed

---

## Special Functions for Walking

Some walking actions have special handling:

### Continuous Walking

Actions like `'go_forward'`, `'go_forward_fast'`, `'go_forward_slow'`, `'back'`, and `'back_fast'` have special start/end handling:

- They automatically call `'go_forward_start'` or `'back_start'` when first run
- They automatically call `'go_forward_end'` or `'back_end'` when stopped
- This ensures smooth transitions

### Example: Continuous Walking Loop

```python
import hiwonder.ActionGroupControl as AGC
import time
import threading

# Start continuous walk
print("Starting walk...")
walk_thread = threading.Thread(
    target=AGC.runActionGroup,
    args=('go_forward', 0),  # 0 = infinite
    daemon=True
)
walk_thread.start()

# Walk for 5 seconds
time.sleep(5)

# Stop (will automatically run 'go_forward_end')
print("Stopping...")
AGC.stopActionGroup()
```

---

## Stopping Actions

### Stop Current Action

```python
from hiwonder.ActionGroupControl import stopAction, stopActionGroup

# Stop single action
stopAction()

# Stop action group (recommended for walking)
stopActionGroup()
```

---

## Complete Example Script

```python
#!/usr/bin/env python3
# encoding: utf-8
"""
Complete example showing all available preprogrammed actions
"""

import sys
import time
import hiwonder.ros_robot_controller_sdk as rrc
from hiwonder.Controller import Controller
import hiwonder.ActionGroupControl as AGC

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

# Initialize
board = rrc.Board()
ctl = Controller(board)
ctl.enable_recv()

# Center head
ctl.set_pwm_servo_pulse(1, 1500, 500)
ctl.set_pwm_servo_pulse(2, 1500, 500)
time.sleep(0.5)

# Stand
print("Standing...")
AGC.runActionGroup('stand_slow', times=1)
time.sleep(2)

# Movement examples
print("\n=== Movement Examples ===")

print("Walking forward...")
AGC.runActionGroup('go_forward', times=3, with_stand=True)
time.sleep(1)

print("Turning left...")
AGC.runActionGroup('turn_left', times=1)
time.sleep(1)

print("Walking forward again...")
AGC.runActionGroup('go_forward', times=2, with_stand=True)
time.sleep(1)

# Gesture examples
print("\n=== Gesture Examples ===")

print("Waving...")
AGC.runActionGroup('wave', times=3)
time.sleep(1)

print("Bowing...")
AGC.runActionGroup('bow', times=1)
time.sleep(1)

print("Celebration pose...")
AGC.runActionGroup('chest', times=1)
time.sleep(1)

# Exercise examples
print("\n=== Exercise Examples ===")

print("Doing push-ups...")
AGC.runActionGroup('push_ups', times=3)
time.sleep(1)

print("Doing squats...")
AGC.runActionGroup('squat', times=3)
time.sleep(1)

# Final stand
print("\nReturning to stand position...")
AGC.runActionGroup('stand_slow', times=1)

print("\nAll actions complete!")
```

---

## Tips

1. **Always start with `'stand_slow'`** to ensure the robot is in a known good position
2. **Use `with_stand=True`** for walking actions to ensure the robot ends in a stable position
3. **Add `time.sleep()` between actions** to allow the robot to complete each movement
4. **For continuous walking**, use threading and `stopActionGroup()` to control duration
5. **Check action files exist** - Action files must be in `/home/pi/TonyPi/ActionGroups/` as `.d6a` files
6. **Some actions may not exist** - Not all robots have all action files. Check which ones are available on your system.

---

## Finding Available Actions

To see which action files you actually have on your system:

```bash
ls /home/pi/TonyPi/ActionGroups/*.d6a
```

Then use those action names (without the `.d6a` extension) in your code.

