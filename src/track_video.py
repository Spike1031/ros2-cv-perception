from pathlib import Path
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = PROJECT_ROOT / "data" / "input.mp4"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

model = YOLO("yolov8n.pt")

model.track(
    source=str(VIDEO_PATH),
    save=True,
    project=str(OUTPUT_DIR),
    name="tracking_video",
    exist_ok=True,
    conf=0.3,
    imgsz=640,
    tracker="bytetrack.yaml",
    vid_stride=2
)

print("Tracking finished.")