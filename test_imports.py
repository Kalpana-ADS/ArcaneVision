
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

print("Testing imports...")
try:
    import cv2
    print("OK: cv2 imported successfully")
except ImportError as e:
    print(f"ERROR: cv2 import failed: {e}")

try:
    import mediapipe
    print("OK: mediapipe imported successfully")
except ImportError as e:
    print(f"ERROR: mediapipe import failed: {e}")

try:
    import numpy
    print("OK: numpy imported successfully")
except ImportError as e:
    print(f"ERROR: numpy import failed: {e}")

try:
    import pygame
    print("OK: pygame imported successfully")
except ImportError as e:
    print(f"ERROR: pygame import failed: {e}")

print("\nTesting project imports...")
try:
    from src.core.engine import Engine
    print("OK: Engine imported successfully")
except Exception as e:
    print(f"ERROR: Engine import failed: {e}")
    import traceback
    traceback.print_exc()
