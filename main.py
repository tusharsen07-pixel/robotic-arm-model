"""
main.py — Main Entry Point for AI Robotic Arm System

Architecture Flow:
VOICE / TEXT INPUT
       ↓
LOCAL COMMAND PARSER (No LLM / No Gemini required)
       ↓
STRUCTURED INTENT
       ↓
[DOWNSTREAM PHASES: Vision / Coordinates / IK / Safety / ESP32]

Usage:
  Interactive Mode:
    python main.py
  Single Command:
    python main.py --cmd "Pick up the red bottle"
  Run Test Suite:
    python main.py --test
"""

import sys
import json
import argparse
from typing import Dict, Any, List

import config
from ai.command_parser import CommandParser, parse_command
from ai.intents import (
    ACTION_OPEN_GRIPPER,
    ACTION_CLOSE_GRIPPER,
    ACTION_MOVE_HOME,
    ACTION_ROTATE_BASE,
    ACTION_PICK,
    ACTION_PLACE,
    ACTION_STOP_ARM,
    ACTION_UNKNOWN,
)


def run_test_suite() -> bool:
    """Run all required test commands and verify their structured outputs."""
    parser = CommandParser()

    test_cases: List[Dict[str, Any]] = [
        {
            "input": "Open the gripper",
            "expected": {
                "action": ACTION_OPEN_GRIPPER,
                "parameters": {},
            },
        },
        {
            "input": "Close the gripper",
            "expected": {
                "action": ACTION_CLOSE_GRIPPER,
                "parameters": {},
            },
        },
        {
            "input": "Move to home position",
            "expected": {
                "action": ACTION_MOVE_HOME,
                "parameters": {},
            },
        },
        {
            "input": "Rotate the base 30 degrees",
            "expected": {
                "action": ACTION_ROTATE_BASE,
                "parameters": {"angle": 30},
            },
        },
        {
            "input": "Pick up the bottle",
            "expected": {
                "action": ACTION_PICK,
                "parameters": {"object": "bottle"},
            },
        },
        {
            "input": "Pick up the red bottle",
            "expected": {
                "action": ACTION_PICK,
                "parameters": {"object": "bottle", "color": "red"},
            },
        },
        {
            "input": "Place the object on the left",
            "expected": {
                "action": ACTION_PLACE,
                "parameters": {"location": "left"},
            },
        },
        {
            "input": "Stop the arm",
            "expected": {
                "action": ACTION_STOP_ARM,
                "parameters": {},
            },
        },
    ]

    print("=" * 60)
    print("RUNNING LOCAL COMMAND PARSER TEST SUITE")
    print("=" * 60)

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        cmd = test["input"]
        expected = test["expected"]
        result = parser.parse(cmd).to_dict()

        is_match = (
            result.get("action") == expected.get("action")
            and result.get("parameters") == expected.get("parameters")
        )

        print(f"\n[TEST {i}]")
        print(f"INPUT:    \"{cmd}\"")
        print("OUTPUT:  ", json.dumps(result, indent=4))

        if is_match:
            print("STATUS:   PASS")
        else:
            print(f"STATUS:   FAIL (Expected: {json.dumps(expected)})")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED SUCCESSFULLY (8/8)")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    return all_passed


def process_command(command_text: str, parser: CommandParser) -> Dict[str, Any]:
    """Process an input command through the local pipeline and print structured intent."""
    intent = parser.parse(command_text)
    structured_dict = intent.to_dict()

    print(f"\nCommand: {command_text}")
    print("Structured Intent:")
    print(json.dumps(structured_dict, indent=4))

    # Architectural routing simulation (No physical hardware movement)
    action = structured_dict.get("action")
    params = structured_dict.get("parameters", {})

    if action == ACTION_OPEN_GRIPPER:
        print("[SIMULATION] Action: Open gripper")
    elif action == ACTION_CLOSE_GRIPPER:
        print("[SIMULATION] Action: Close gripper")
    elif action == ACTION_MOVE_HOME:
        print("[SIMULATION] Action: Move to home pose")
    elif action == ACTION_ROTATE_BASE:
        print(f"[SIMULATION] Action: Rotate base by {params.get('angle')} degrees")
    elif action == ACTION_PICK:
        color_info = f" (color: {params.get('color')})" if 'color' in params else ""
        print(f"[SIMULATION] Action: Pick target '{params.get('object')}'{color_info}")
        print("[SIMULATION] Downstream vision pipeline will localize object coordinates.")
    elif action == ACTION_PLACE:
        print(f"[SIMULATION] Action: Place object at '{params.get('location')}'")
    elif action == ACTION_STOP_ARM:
        print("[SIMULATION] Action: STOP ARM (Safety Emergency Stop triggered)")
    elif action == ACTION_UNKNOWN:
        print(f"[SIMULATION] Action: Unknown command. Error: {intent.error}")

    return structured_dict


def interactive_mode(parser: CommandParser) -> None:
    """Run interactive terminal prompt for command input."""
    print("=" * 60)
    print(" AI ROBOTIC ARM — LOCAL COMMAND PARSER (TERMINAL)")
    print(f" Simulation Mode: {config.SIMULATION_MODE} | Cloud Gemini: NOT REQUIRED")
    print(" Type a command to test (or 'exit' / 'quit' to exit)")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nEnter command: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Exiting.")
                break
            process_command(user_input, parser)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Robotic Arm Local Controller")
    parser.add_argument(
        "--cmd",
        type=str,
        help="Single command to parse and process",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the test suite on all supported commands",
    )

    args = parser.parse_args()
    cmd_parser = CommandParser()

    if args.test:
        success = run_test_suite()
        sys.exit(0 if success else 1)
    elif args.cmd:
        process_command(args.cmd, cmd_parser)
    else:
        interactive_mode(cmd_parser)


if __name__ == "__main__":
    main()
