from collections import Counter, defaultdict, deque

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ultralytics import YOLO


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

MAX_TRAJECTORY_LENGTH = 30

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

    frame_h, frame_w = frame.shape[:2]

    (text_w, text_h), baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness,
    )

    x = max(0, min(x, frame_w - text_w - 20))
    label_y = max(y, text_h + baseline + 10)

    cv2.rectangle(
        frame,
        (x, label_y - text_h - baseline - 8),
        (x + text_w + 12, label_y + 4),
        (255, 255, 255),
        -1,
    )

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
    font_scale = PANEL_FONT_SCALE
    thickness = PANEL_THICKNESS

    if current_counts:
        current_text = "Current objects: " + ", ".join(
            [f"{k}:{v}" for k, v in current_counts.items()]
        )
    else:
        current_text = "Current objects: 0"

    if unique_ids_by_class:
        unique_text = "Unique tracked: " + ", ".join(
            [f"{k}:{len(v)}" for k, v in unique_ids_by_class.items()]
        )
    else:
        unique_text = "Unique tracked: 0"

    panel_lines = [
        f"Frame: {frame_id}",
        current_text,
        unique_text,
    ]

    max_text_w = 0
    for line in panel_lines:
        (text_w, _), _ = cv2.getTextSize(line, font, font_scale, thickness)
        max_text_w = max(max_text_w, text_w)

    panel_w = max_text_w + 50
    panel_h = line_h * len(panel_lines) + 25

    cv2.rectangle(
        frame,
        (10, 10),
        (panel_w, panel_h),
        (0, 0, 0),
        -1,
    )

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


class TrafficPerceptionNode(Node):
    def __init__(self):
        super().__init__("traffic_perception_node")

        self.bridge = CvBridge()
        self.model = YOLO(MODEL_NAME)

        self.frame_id = 0
        self.trajectories = defaultdict(lambda: deque(maxlen=MAX_TRAJECTORY_LENGTH))
        self.unique_ids_by_class = defaultdict(set)

        self.image_subscription = self.create_subscription(
            Image,
            "/image_raw",
            self.image_callback,
            10,
        )

        self.annotated_image_publisher = self.create_publisher(
            Image,
            "/traffic_perception/annotated_image",
            10,
        )

        self.summary_publisher = self.create_publisher(
            String,
            "/traffic_perception/summary",
            10,
        )

        self.get_logger().info("Traffic perception node started.")
        self.get_logger().info("Subscribed to: /image_raw")
        self.get_logger().info("Publishing annotated images to: /traffic_perception/annotated_image")
        self.get_logger().info("Publishing summaries to: /traffic_perception/summary")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        self.frame_id += 1

        current_counts = Counter()

        results = self.model.track(
            frame,
            conf=CONF_THRES,
            imgsz=IMG_SIZE,
            tracker=TRACKER_CONFIG,
            persist=True,
            verbose=False,
        )

        result = results[0]
        names = self.model.names

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
                self.unique_ids_by_class[class_name].add(track_id)
                self.trajectories[track_id].append((center_x, center_y))

                color = get_color(track_id)

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color,
                    BOX_THICKNESS,
                )

                label = f"ID {track_id} {class_name} {confidence:.2f}"
                draw_label(frame, label, x1, y1, color)

                points = list(self.trajectories[track_id])
                if (
                    SHOW_TRAJECTORY
                    and class_name in DRAW_TRAJECTORY_CLASSES
                    and len(points) >= 8
                ):
                    for i in range(1, len(points)):
                        cv2.line(
                            frame,
                            points[i - 1],
                            points[i],
                            color,
                            2,
                        )

        draw_count_panel(
            frame,
            self.frame_id,
            current_counts,
            self.unique_ids_by_class,
        )

        annotated_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.annotated_image_publisher.publish(annotated_msg)

        summary_msg = String()
        summary_msg.data = self.build_summary_text(current_counts)
        self.summary_publisher.publish(summary_msg)

        if self.frame_id % 30 == 0:
            self.get_logger().info(summary_msg.data)

    def build_summary_text(self, current_counts):
        current_text = ", ".join(
            [f"{k}:{v}" for k, v in current_counts.items()]
        ) if current_counts else "0"

        unique_text = ", ".join(
            [f"{k}:{len(v)}" for k, v in self.unique_ids_by_class.items()]
        ) if self.unique_ids_by_class else "0"

        return (
            f"Frame {self.frame_id} | "
            f"Current objects: {current_text} | "
            f"Unique tracked: {unique_text}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = TrafficPerceptionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()