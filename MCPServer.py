#!/usr/bin/env python3
# encoding: utf-8
"""
MCP server entrypoint for TonyPi RobotController tools.

This exposes a curated allowlist of RobotController methods for LLM/MCP use.
"""

import base64
import sys

from mcp.server.fastmcp import FastMCP

from RobotController import get_robot


if sys.version_info.major == 2:
    print("Please run this program with python3!")
    sys.exit(0)


mcp = FastMCP("TonyPi")
robot = get_robot()


@mcp.tool()
def stand(slow: bool = True):
    """Stand at attention."""
    return robot.stand(slow=slow)


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
    return robot.camera_open()


@mcp.tool()
def camera_close():
    """Close the camera."""
    return robot.camera_close()


@mcp.tool()
def get_camera_frame_info():
    """Get camera frame metadata (shape/size only)."""
    return robot.get_camera_frame()


@mcp.tool()
def get_camera_frame_base64():
    """Get current camera frame encoded as base64 JPEG."""
    ok, frame = robot.get_camera_frame_array()
    if not ok or frame is None:
        return {"success": False, "error": "No frame available"}
    try:
        import cv2

        ret, buf = cv2.imencode(".jpg", frame)
        if not ret:
            return {"success": False, "error": "Failed to encode frame"}
        encoded = base64.b64encode(buf.tobytes()).decode("ascii")
        return {"success": True, "image_b64": encoded, "format": "jpeg"}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    mcp.run()
