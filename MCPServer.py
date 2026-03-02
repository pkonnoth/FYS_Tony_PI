#!/usr/bin/env python3
# encoding: utf-8
"""
MCP server entrypoint for TonyPi RobotController tools.

This exposes a curated allowlist of RobotController methods for LLM/MCP use.
"""

import base64
import os
import sys
import time
import urllib.request

from mcp.server.fastmcp import FastMCP

from RobotController import get_robot


if sys.version_info.major == 2:
    print("Please run this program with python3!")
    sys.exit(0)


mcp = FastMCP("TonyPi")
robot = get_robot()

_CAMERA_FRAMES_DIR = "camera_frames"
_MJPG_SNAPSHOT_URL = os.environ.get(
    "MJPG_SNAPSHOT_URL", "http://127.0.0.1:8080/?action=snapshot"
)


def _ensure_camera_frames_dir() -> str:
    os.makedirs(_CAMERA_FRAMES_DIR, exist_ok=True)
    return _CAMERA_FRAMES_DIR


def _save_frame_bytes(encoded_bytes: bytes) -> tuple[str, str]:
    frames_dir = _ensure_camera_frames_dir()
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    millis = int((time.time() % 1) * 1000)
    filename = f"frame_{timestamp}_{millis:03d}.jpg"
    file_path = os.path.join(frames_dir, filename)
    with open(file_path, "wb") as out_file:
        out_file.write(encoded_bytes)
    return filename, file_path


def _read_mjpg_snapshot_bytes(timeout_s: float = 1.5):
    try:
        with urllib.request.urlopen(_MJPG_SNAPSHOT_URL, timeout=timeout_s) as resp:
            if getattr(resp, "status", 200) != 200:
                return None
            data = resp.read()
            if data:
                return data
    except Exception:
        return None
    return None


def _mjpg_snapshot_available(timeout_s: float = 1.0) -> bool:
    return _read_mjpg_snapshot_bytes(timeout_s=timeout_s) is not None


@mcp.tool()
def stand(slow: bool = True):
    """Stand at attention."""
    return robot.stand(slow=slow)


@mcp.tool()
def run_action(action_name: str, times: int = 1, with_stand: bool = False):
    """Run a named action group directly."""
    return robot.run_action(
        action_name=action_name,
        times=times,
        with_stand=with_stand,
    )


@mcp.tool()
def run_action_async(action_name: str, times: int = 1, with_stand: bool = False):
    """Run a named action group asynchronously."""
    return robot.run_action_async(
        action_name=action_name,
        times=times,
        with_stand=with_stand,
    )


@mcp.tool()
def walk_forward(steps: int = 1, speed: str = "normal", with_stand: bool = True):
    """Walk forward using action groups."""
    return robot.walk_forward(steps=steps, speed=speed, with_stand=with_stand)


@mcp.tool()
def walk_backward(steps: int = 1, fast: bool = False, with_stand: bool = True):
    """Walk backward using action groups."""
    return robot.walk_backward(steps=steps, fast=fast, with_stand=with_stand)


@mcp.tool()
def turn_left(times: int = 1):
    """Turn left."""
    return robot.turn_left(times=times)


@mcp.tool()
def turn_right(times: int = 1):
    """Turn right."""
    return robot.turn_right(times=times)


@mcp.tool()
def move_left(steps: int = 1, fast: bool = False):
    """Move left."""
    return robot.move_left(steps=steps, fast=fast)


@mcp.tool()
def move_right(steps: int = 1, fast: bool = False):
    """Move right."""
    return robot.move_right(steps=steps, fast=fast)


@mcp.tool()
def step_in_place(times: int = 10):
    """March in place."""
    return robot.step_in_place(times=times)


@mcp.tool()
def wave(times: int = 3):
    """Wave hand."""
    return robot.wave(times=times)


@mcp.tool()
def bow(times: int = 1):
    """Bow."""
    return robot.bow(times=times)


@mcp.tool()
def celebrate():
    """Celebration pose."""
    return robot.celebrate()


@mcp.tool()
def twist(times: int = 5):
    """Twist waist."""
    return robot.twist(times=times)


@mcp.tool()
def push_ups(times: int = 3):
    """Do push-ups."""
    return robot.push_ups(times=times)


@mcp.tool()
def sit_ups(times: int = 3):
    """Do sit-ups."""
    return robot.sit_ups(times=times)


@mcp.tool()
def squat(times: int = 5):
    """Squat."""
    return robot.squat(times=times)


@mcp.tool()
def weightlifting():
    """Weightlifting pose."""
    return robot.weightlifting()


@mcp.tool()
def kick_left(fast: bool = False):
    """Left kick."""
    return robot.kick_left(fast=fast)


@mcp.tool()
def kick_right(fast: bool = False):
    """Right kick."""
    return robot.kick_right(fast=fast)


@mcp.tool()
def punch_left():
    """Left hook punch."""
    return robot.punch_left()


@mcp.tool()
def punch_right():
    """Right hook punch."""
    return robot.punch_right()


@mcp.tool()
def wing_chun():
    """Wing Chun martial arts moves."""
    return robot.wing_chun()


@mcp.tool()
def stand_up_from_front():
    """Stand up from front fall."""
    return robot.stand_up_from_front()


@mcp.tool()
def stand_up_from_back():
    """Stand up from back fall."""
    return robot.stand_up_from_back()


@mcp.tool()
def stop_action():
    """Stop any running action group."""
    return robot.stop_action()


@mcp.tool()
def set_bus_servo(servo_id: int, position: int, duration_ms: int = 500):
    """Set a bus servo position (1-18, 0-500)."""
    return robot.set_bus_servo(
        servo_id=servo_id, position=position, duration_ms=duration_ms
    )


@mcp.tool()
def set_head_pan(position: int, duration_ms: int = 500):
    """Set head pan (PWM servo 1)."""
    return robot.set_head_pan(position=position, duration_ms=duration_ms)


@mcp.tool()
def set_head_tilt(position: int, duration_ms: int = 500):
    """Set head tilt (PWM servo 2)."""
    return robot.set_head_tilt(position=position, duration_ms=duration_ms)


@mcp.tool()
def center_head(duration_ms: int = 500):
    """Center head pan/tilt."""
    return robot.center_head(duration_ms=duration_ms)


@mcp.tool()
def look_at(pan: int, tilt: int, duration_ms: int = 500):
    """Set head to specific pan/tilt positions."""
    return robot.look_at(pan=pan, tilt=tilt, duration_ms=duration_ms)


@mcp.tool()
def get_imu():
    """Read IMU data."""
    return robot.get_imu()


@mcp.tool()
def get_battery_voltage():
    """Read battery voltage."""
    return robot.get_battery_voltage()


@mcp.tool()
def get_servo_temperature(servo_id: int):
    """Read bus servo temperature."""
    return robot.get_servo_temperature(servo_id=servo_id)


@mcp.tool()
def get_servo_voltage(servo_id: int):
    """Read bus servo voltage."""
    return robot.get_servo_voltage(servo_id=servo_id)


@mcp.tool()
def get_status():
    """Get overall robot status."""
    return robot.get_status()


@mcp.tool()
def shutdown():
    """Stop actions and return to safe pose."""
    return robot.shutdown()


@mcp.tool()
def camera_open():
    """Open the camera."""
    if _mjpg_snapshot_available():
        return {
            "success": True,
            "message": "Using MJPG snapshot source",
            "source": "mjpg_snapshot",
        }
    return robot.camera_open()


@mcp.tool()
def camera_close():
    """Close the camera."""
    if _mjpg_snapshot_available():
        return {
            "success": True,
            "message": "MJPG snapshot source active; no direct camera close needed",
            "source": "mjpg_snapshot",
        }
    return robot.camera_close()


@mcp.tool()
def get_camera_frame_info():
    """Get camera frame metadata (shape/size only)."""
    snapshot = _read_mjpg_snapshot_bytes(timeout_s=1.0)
    if snapshot is not None:
        return {
            "success": True,
            "frame_available": True,
            "source": "mjpg_snapshot",
            "bytes": len(snapshot),
            "format": "jpeg",
        }
    return robot.get_camera_frame()


@mcp.tool()
def get_camera_frame_base64():
    """Get current camera frame, save to disk, and return base64 JPEG."""
    try:
        source = "robot_camera"
        encoded_bytes = None
        camera_opened = False

        if robot.camera is not None and getattr(robot.camera, "opened", False):
            ok, frame = robot.get_camera_frame_array()
            if ok and frame is not None:
                import cv2

                ret, buf = cv2.imencode(".jpg", frame)
                if ret:
                    encoded_bytes = buf.tobytes()

        if encoded_bytes is None:
            snapshot = _read_mjpg_snapshot_bytes()
            if snapshot is not None:
                encoded_bytes = snapshot
                source = "mjpg_snapshot"

        if encoded_bytes is None:
            open_result = robot.camera_open()
            if not open_result.get("success"):
                return {
                    "success": False,
                    "error": open_result.get("error", "Camera open failed"),
                }
            camera_opened = True
            ok, frame = robot.get_camera_frame_array()
            if not ok or frame is None:
                return {"success": False, "error": "No frame available"}
            import cv2

            ret, buf = cv2.imencode(".jpg", frame)
            if not ret:
                return {"success": False, "error": "Failed to encode frame"}
            encoded_bytes = buf.tobytes()

        filename, file_path = _save_frame_bytes(encoded_bytes)
        encoded = base64.b64encode(encoded_bytes).decode("ascii")
        result = {
            "success": True,
            "image_b64": encoded,
            "format": "jpeg",
            "file": filename,
            "path": file_path,
            "source": source,
        }
        if camera_opened:
            result["camera_opened"] = True
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
