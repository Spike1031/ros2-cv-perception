from collections import Counter, defaultdict, deque
from pathlib import Path
import csv
import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[1]

VIDEO_PATH = PROJECT_ROOT / "data" / "input.mp4"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "traffic_perception_demo"
OUTPUT_VIDEO_PATH = OUTPUT_DIR / "traffic_perception_demo.mp4"
OUTPUT_CSV_PATH = OUTPUT_DIR / "tracking_results.csv"

MODEL_NAME = "yolov8n.pt"
CONF_THRES = 0.3
IMG_SIZE = 640
TRACKER_CONFIG = "bytetrack.yaml"

SHOW_TRAJECTORY = False

BOX_THICKNESS = 4
LABEL_FONT_SCALE = 1.2
LABEL_THICKNESS = 3

PANEL_FONT_SCALE = 0.9
PANEL_THICKNESS = 2

# 只保留交通/自动驾驶相关类别，避免把杯子、椅子之类也统计进去
TRAFFIC_CLASSES = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "traffic light",
    "stop sign",
}


DRAW_TRAJECTORY_CLASSES = {
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "bus",
    "truck",
}


# 每个目标最多保留最近多少帧轨迹点
MAX_TRAJECTORY_LENGTH = 30


def get_color(track_id: int):
    """Generate a stable color for each tracking ID."""
    return (
        int((track_id * 37) % 255),
        int((track_id * 17) % 255),
        int((track_id * 29) % 255),
    )


def draw_label(frame, text, x, y, color):
    """Draw a large readable label above the bounding box."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = LABEL_FONT_SCALE
    thickness = LABEL_THICKNESS

    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

    # Make sure the label is not outside the top boundary
    label_y = max(y, text_h + baseline + 10)

    # White label background for clearer visualization
    cv2.rectangle(
        frame,
        (x, label_y - text_h - baseline - 8),
        (x + text_w + 12, label_y + 4),
        (255, 255, 255),
        -1,
    )

    # Text color uses the object color
    cv2.putText(
        frame,
        text,
        (x + 6, label_y - 7),
        font,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def draw_count_panel(frame, frame_id, current_counts, unique_ids_by_class):
    """Draw current-frame counts and unique tracked-object counts."""
    x0, y0 = 25, 45
    line_h = 45

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.1
    thickness = 2

    panel_lines = [
        f"Frame: {frame_id}",
        "Current objects: "
        + ", ".join([f"{k}:{v}" for k, v in current_counts.items()])
        if current_counts
        else "Current objects: 0",
        "Unique tracked: "
        + ", ".join([f"{k}:{len(v)}" for k, v in unique_ids_by_class.items()])
        if unique_ids_by_class
        else "Unique tracked: 0",
    ]

    # 根据文字长度自动计算面板宽度
    max_text_w = 0
    for line in panel_lines:
        (text_w, _), _ = cv2.getTextSize(line, font, font_scale, thickness)
        max_text_w = max(max_text_w, text_w)

    panel_w = max_text_w + 50
    panel_h = line_h * len(panel_lines) + 25

    cv2.rectangle(frame, (10, 10), (panel_w, panel_h), (0, 0, 0), -1)

    for i, line in enumerate(panel_lines):
        cv2.putText(
            frame,
            line,
            (x0, y0 + i * line_h),
            font,
            font_scale,
            (0, 255, 255),
            thickness,
            cv2.LINE_AA,
        )


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not VIDEO_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find input video: {VIDEO_PATH}\n"
            f"Put your traffic-scene video at data/input.mp4"
        )

    model = YOLO(MODEL_NAME)
    names = model.names

    cap = cv2.VideoCapture(str(VIDEO_PATH))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {VIDEO_PATH}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 25

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter.fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(OUTPUT_VIDEO_PATH), fourcc, fps, (width, height))

    trajectories = defaultdict(lambda: deque(maxlen=MAX_TRAJECTORY_LENGTH))
    unique_ids_by_class = defaultdict(set)

    with open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(
            [
                "frame_id",
                "track_id",
                "class_name",
                "confidence",
                "x1",
                "y1",
                "x2",
                "y2",
                "center_x",
                "center_y",
            ]
        )

        frame_id = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_id += 1
            current_counts = Counter()

            results = model.track(
                frame,
                conf=CONF_THRES,
                imgsz=IMG_SIZE,
                tracker=TRACKER_CONFIG,
                persist=True,
                verbose=False,
            )

            result = results[0]

            if result.boxes is not None:
                for box in result.boxes:
                    if box.id is None:
                        continue

                    class_id = int(box.cls[0])
                    class_name = names[class_id]

                    if class_name not in TRAFFIC_CLASSES:
                        continue

                    track_id = int(box.id[0])
                    confidence = float(box.conf[0])

                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    current_counts[class_name] += 1
                    unique_ids_by_class[class_name].add(track_id)
                    trajectories[track_id].append((center_x, center_y))

                    color = get_color(track_id)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, BOX_THICKNESS)
                    label = f"ID {track_id} {class_name} {confidence:.2f}"
                    draw_label(frame, label, x1, y1, color)

                    points = list(trajectories[track_id])
                    if SHOW_TRAJECTORY and class_name in DRAW_TRAJECTORY_CLASSES and len(points) >= 8:
                        for i in range(1, len(points)):
                            cv2.line(frame, points[i - 1], points[i], color, 2)

                    csv_writer.writerow(
                        [
                            frame_id,
                            track_id,
                            class_name,
                            round(confidence, 4),
                            x1,
                            y1,
                            x2,
                            y2,
                            center_x,
                            center_y,
                        ]
                    )

            draw_count_panel(frame, frame_id, current_counts, unique_ids_by_class)
            writer.write(frame)

            if frame_id % 50 == 0:
                print(f"Processed {frame_id} frames...")

    cap.release()
    writer.release()

    print("Traffic perception demo finished.")
    print(f"Output video: {OUTPUT_VIDEO_PATH}")
    print(f"Output CSV: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()