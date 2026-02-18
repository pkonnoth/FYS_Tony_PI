#!/usr/bin/env python3
# encoding: utf-8
import argparse
import base64
import sys

import cv2


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture a frame and print base64")
    parser.add_argument("--device", type=int, default=0, help="Camera index")
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Optional frame width (pixels)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Optional frame height (pixels)",
    )
    parser.add_argument(
        "--format",
        default="jpg",
        choices=("jpg", "png"),
        help="Output image format",
    )
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.device)
    if args.width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    if args.height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)

    if not cap.isOpened():
        print(f"Failed to open camera device {args.device}", file=sys.stderr)
        return 1

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        print("Failed to read frame from camera", file=sys.stderr)
        return 1

    ext = "." + args.format
    ok, encoded = cv2.imencode(ext, frame)
    if not ok:
        print("Failed to encode frame", file=sys.stderr)
        return 1

    b64 = base64.b64encode(encoded.tobytes()).decode("ascii")
    print(b64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
