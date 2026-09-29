"""
test_camera.py — Continuous Live Camera Preview with YOLOv8n Detection.

Continuously captures frames in a loop, runs YOLOv8n (320x320),
draws bounding boxes, and displays live frames with cv2.imshow("YOLOv8n Camera", frame).
Keeps the window open continuously until the user presses 'q'.
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from vision.detection import ObjectDetector

# ---------------------------------------------------------------------------
# Ensure cv2.imshow / cv2.waitKey / cv2.destroyAllWindows open a live visible
# window on all Windows environments (including headless / Windows N)
# ---------------------------------------------------------------------------
_USE_NATIVE_HIGHGUI = False
try:
    cv2.namedWindow("_probe", cv2.WINDOW_AUTOSIZE)
    cv2.destroyAllWindows()
    _USE_NATIVE_HIGHGUI = True
except (cv2.error, AttributeError):
    _USE_NATIVE_HIGHGUI = False

if not _USE_NATIVE_HIGHGUI:
    import tkinter as tk
    from PIL import Image, ImageTk

    class _GUIWindow:
        def __init__(self, title: str):
            self.root = tk.Tk()
            self.root.title(title)
            self.root.resizable(False, False)
            self.label = tk.Label(self.root, bg="black")
            self.label.pack()
            self.last_key = -1
            self.closed = False
            self.root.bind("<Key>", self._on_key)
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)

            # Bring preview window to the front
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(100, lambda: self.root.attributes("-topmost", False))
            self.root.focus_force()

        def _on_key(self, event):
            if event.char:
                self.last_key = ord(event.char.lower())
            elif event.keysym == "Escape":
                self.last_key = ord("q")

        def _on_close(self):
            self.last_key = ord("q")
            self.closed = True

        def show(self, bgr_img: np.ndarray):
            if self.closed:
                return
            rgb = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)
            try:
                self.root.update_idletasks()
            except Exception:
                self.closed = True

        def wait_key(self, delay: int = 1) -> int:
            if self.closed:
                return ord("q")
            try:
                self.root.update()
            except Exception:
                self.closed = True
                return ord("q")
            k = self.last_key
            self.last_key = -1
            return k

        def destroy(self):
            if not self.closed:
                self.closed = True
                try:
                    self.root.destroy()
                except Exception:
                    pass

    _active_windows = {}

    def _compat_imshow(win_name: str, mat: np.ndarray):
        if win_name not in _active_windows or _active_windows[win_name].closed:
            _active_windows[win_name] = _GUIWindow(win_name)
        _active_windows[win_name].show(mat)

    def _compat_wait_key(delay: int = 1) -> int:
        ret_key = -1
        for win in list(_active_windows.values()):
            k = win.wait_key(delay)
            if k != -1:
                ret_key = k
        if not _active_windows:
            time.sleep(max(delay, 1) / 1000.0)
        return ret_key

    def _compat_destroy_all_windows():
        for win in list(_active_windows.values()):
            win.destroy()
        _active_windows.clear()

    cv2.imshow = _compat_imshow
    cv2.waitKey = _compat_wait_key
    cv2.destroyAllWindows = _compat_destroy_all_windows


def open_camera():
    """Probe camera indices and return the working VideoCapture."""
    for idx in [1, 0, 2, 3]:
        cap = cv2.VideoCapture(idx)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None and frame.size > 0:
                print(f"Connected to camera on index {idx}")
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                return cap
            cap.release()
    return None


def main():
    # 1. Open USB/UVC camera
    cap = open_camera()
    if cap is None:
        print("Failed to open USB camera")
        return

    # 2. Load existing YOLOv8n detector (320x320 inference)
    detector = ObjectDetector(conf_threshold=0.25, imgsz=320)
    print("Live preview active. Press 'q' inside window to exit.")

    # 3. Continuous frame capture loop
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read camera frame")
            break

        # Run existing YOLOv8n detection (320x320)
        detections = detector.detect(frame, imgsz=320)

        # Draw YOLO bounding boxes on frame
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cls_name = det["class"]
            conf = det["confidence"]
            cx, cy = det["center"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
            label = f"{cls_name} {conf:.2f} ({cx},{cy})"
            cv2.putText(
                frame,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

        # 4. Show the live frame
        cv2.imshow("YOLOv8n Camera", frame)

        # 5. Check if 'q' was pressed
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("'q' pressed. Closing camera...")
            break

    # 6. Release camera and destroy windows
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released and preview closed.")


if __name__ == "__main__":
    main()
