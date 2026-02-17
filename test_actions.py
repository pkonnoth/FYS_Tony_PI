#!/usr/bin/env python3
# encoding: utf-8
import time
import sys
import os

# Ensure we can import RobotController
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from RobotController import get_robot

def test_actions():
    print("Initializing RobotController...")
    robot = get_robot()
    print("Robot initialized.")

    # Helper to run and log action
    def run_test(name, func, **kwargs):
        print(f"\nTesting {name}...")
        try:
            result = func(**kwargs)
            print(f"{name} result: {result}")
            # Wait a bit between actions to ensure completion/stability
            time.sleep(2) 
        except Exception as e:
            print(f"Error running {name}: {e}")

    # Initial Reset to ensure robot is in a known state
    run_test("Initial Reset", robot.shutdown)

    # Do 1 sit-up
    run_test("Sit Ups", robot.sit_ups, times=1)

    # Do 1 push-up
    run_test("Push Ups", robot.push_ups, times=1)

    # Walk forward (normal speed) then stand for stability
    run_test("Walk Forward", robot.walk_forward, steps=3, speed="normal", with_stand=True)
    
    # Relax servos at the end so they are movable
    run_test("Relax Servos", robot.relax)

    print("\nTest sequence complete.")

if __name__ == "__main__":
    try:
        test_actions()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
