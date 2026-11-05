"""Tests for the posture geometry. Run with:  python -m pytest  (or python test_geometry.py)"""
import math

from posture_neckline import Posture, find_angle, find_distance, measure


def test_distance():
    assert find_distance(0, 0, 3, 4) == 5


def test_vertical_segment_is_zero_degrees():
    # ear directly above the shoulder (image y grows downwards)
    assert abs(find_angle(100, 400, 100, 300)) < 1e-9


def test_horizontal_segment_is_ninety_degrees():
    assert abs(find_angle(100, 400, 200, 400) - 90) < 1e-9


def test_forty_five_degrees():
    assert abs(find_angle(100, 400, 200, 300) - 45) < 1e-9


def test_guards_against_zero_length():
    assert math.isnan(find_angle(10, 10, 10, 10))


def test_measure_uses_more_visible_side_and_flags_slouch():
    pts = {i: (0.0, 0.0, 0.0) for i in range(33)}
    # left side visible: hip (100,600), shoulder leaning forward (160,400), ear far forward (260,330)
    pts[23], pts[11], pts[7] = (100, 600, 0.9), (160, 400, 0.9), (260, 330, 0.9)
    p = measure(pts)
    assert p.side == "left"
    assert 16 < p.torso < 17.5      # atan(60/200)  ~ 16.7 degrees
    assert 54 < p.neck < 56         # atan(100/70)  ~ 55.0 degrees
    assert not p.good


def test_good_posture():
    assert Posture(neck=10, torso=5, side="left").good


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
