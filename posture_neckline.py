"""Neck and torso inclination from a single camera.

Script version of `Pose Detection-Neckline- Uploading-v0.1.ipynb`.
MediaPipe Pose finds the shoulder, ear and hip; the neck and torso
inclination are measured against a vertical line, the same way as the
notebook's `findAngle()`, and drawn on the frame.

Usage:
    python posture_neckline.py --source Resources/lifting_02.mp4
    python posture_neckline.py --source 0                 # webcam
    python posture_neckline.py --source clip.mp4 --save out.mp4 --no-display
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass

# Posture limits (degrees from vertical). Illustrative values, adjust for your study.
NECK_LIMIT = 40.0
TORSO_LIMIT = 20.0

# MediaPipe Pose landmark indices
LEFT = {"shoulder": 11, "ear": 7, "hip": 23}
RIGHT = {"shoulder": 12, "ear": 8, "hip": 24}

# BGR colours
ORANGE = (0, 127, 255)
YELLOW = (0, 255, 255)
GREEN = (127, 233, 100)
RED = (50, 50, 255)


def find_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def find_angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """Angle in degrees between the segment (x1,y1)->(x2,y2) and a vertical line through (x1,y1).

    Same formula as the notebook's findAngle():
        theta = acos( (y2 - y1) * (-y1) / (|segment| * y1) )
    Fixes from the notebook: uses exact 180/pi (the notebook used int(180/pi) = 57,
    which under-reported every angle by about 0.5%) and guards against division by zero.
    """
    d = find_distance(x1, y1, x2, y2)
    if d == 0 or y1 == 0:
        return float("nan")
    cos_theta = (y2 - y1) * (-y1) / (d * y1)
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))


@dataclass
class Posture:
    neck: float
    torso: float
    side: str

    @property
    def good(self) -> bool:
        return self.neck <= NECK_LIMIT and self.torso <= TORSO_LIMIT


def measure(points: dict[int, tuple[float, float, float]]) -> Posture:
    """points maps landmark index -> (x_px, y_px, visibility). Uses the more visible side."""
    def vis(side: dict[str, int]) -> float:
        return sum(points[i][2] for i in side.values())

    side_name, side = ("left", LEFT) if vis(LEFT) >= vis(RIGHT) else ("right", RIGHT)
    sx, sy, _ = points[side["shoulder"]]
    ex, ey, _ = points[side["ear"]]
    hx, hy, _ = points[side["hip"]]
    return Posture(neck=find_angle(sx, sy, ex, ey), torso=find_angle(hx, hy, sx, sy), side=side_name)


def annotate(frame, points, posture: Posture):
    import cv2  # local import keeps the geometry testable without OpenCV

    side = LEFT if posture.side == "left" else RIGHT
    colour = GREEN if posture.good else RED
    s = tuple(int(v) for v in points[side["shoulder"]][:2])
    e = tuple(int(v) for v in points[side["ear"]][:2])
    h = tuple(int(v) for v in points[side["hip"]][:2])
    ref = 100
    for a, b in [(s, e), (s, (s[0], s[1] - ref)), (h, s), (h, (h[0], h[1] - ref))]:
        cv2.line(frame, a, b, ORANGE if b[0] == a[0] else colour, 4)
    for p in (s, e, h):
        cv2.circle(frame, p, 7, YELLOW, -1)
    cv2.putText(frame, f"Neck {posture.neck:.0f}", (s[0] + 10, s[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
    cv2.putText(frame, f"Torso {posture.torso:.0f}", (h[0] + 10, h[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)
    label = "Good posture" if posture.good else "Check posture"
    cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colour, 2)
    return frame


def run(source: str, save: str | None, display: bool) -> None:
    import cv2
    import mediapipe as mp

    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    if not cap.isOpened():
        raise SystemExit(f"Could not open video source: {source}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Source: {source} | {width}x{height} @ {fps:.0f} FPS")

    writer = None
    if save:
        writer = cv2.VideoWriter(save, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    frames = flagged = 0
    with mp.solutions.pose.Pose(static_image_mode=False) as pose:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frames += 1
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w = frame.shape[:2]
                points = {i: (lm.x * w, lm.y * h, lm.visibility)
                          for i, lm in enumerate(results.pose_landmarks.landmark)}
                posture = measure(points)
                flagged += not posture.good
                annotate(frame, points, posture)
            if writer:
                writer.write(frame)
            if display:
                cv2.imshow("Neckline posture", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    cap.release()
    if writer:
        writer.release()
    if display:
        cv2.destroyAllWindows()
    if frames:
        print(f"Frames: {frames} | flagged for posture: {flagged} ({100 * flagged / frames:.1f}%)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", default="0", help="video file path, or a camera index such as 0")
    parser.add_argument("--save", help="write the annotated video to this .mp4 path")
    parser.add_argument("--no-display", action="store_true", help="don't open a preview window")
    args = parser.parse_args()
    run(args.source, args.save, not args.no_display)


if __name__ == "__main__":
    main()
