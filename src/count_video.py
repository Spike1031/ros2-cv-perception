from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = PROJECT_ROOT / "data" / "input.mp4"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "counting_video"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "counted_video.mp4"

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(str(VIDEO_PATH))

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter.fourcc(*"mp4v")
out = cv2.VideoWriter(str(OUTPUT_PATH), fourcc, fps, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, conf=0.3, imgsz=640)
    result = results[0]

    counter = Counter()
    names = model.names

    for box in result.boxes:
        class_id = int(box.cls[0])
        class_name = names[class_id]
        counter[class_name] += 1

    annotated_frame = result.plot()

    y = 60
    font_scale = 1.4
    thickness = 4
    line_height = 60

    cv2.putText(
        annotated_frame,
        "Object Counts",
        (40, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 255, 0),
        thickness
    )

    for name, count in counter.items():
        y += line_height
        cv2.putText(
            annotated_frame,
            f"{name}: {count}",
            (40, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 255, 0),
            thickness
        )

    out.write(annotated_frame)

cap.release()
out.release()

print(f"Saved to: {OUTPUT_PATH}")