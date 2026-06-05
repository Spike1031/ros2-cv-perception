from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / "data" / "test.jpg"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "counting_image"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

model = YOLO("yolov8n.pt")

results = model(str(IMAGE_PATH), conf=0.3)
result = results[0]

counter = Counter()
names = model.names

for box in result.boxes:
    class_id = int(box.cls[0])
    class_name = names[class_id]
    counter[class_name] += 1

annotated_img = result.plot()

y = 60
font_scale = 1.8
thickness = 5
line_height = 60

cv2.putText(
    annotated_img,
    "Object Counts",
    (40, y),
    cv2.FONT_HERSHEY_SIMPLEX,
    font_scale,
    (0, 255, 0),
    thickness
)

for name, count in counter.items():
    y += line_height
    text = f"{name}: {count}"
    cv2.putText(
        annotated_img,
        text,
        (40, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 255, 0),
        thickness
    )

output_path = OUTPUT_DIR / "counted_result.jpg"
cv2.imwrite(str(output_path), annotated_img)

print("Object counts:")
for name, count in counter.items():
    print(f"{name}: {count}")

print(f"Saved to: {output_path}")