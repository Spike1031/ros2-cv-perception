import rclpy
from std_msgs.msg import String
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__("yolo_detector_node")

        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")
        self.detection_publisher = self.create_publisher(String, "/detections", 10)

        self.subscription = self.create_subscription(
            Image,
            "/image_raw",
            self.image_callback,
            10
        )

        self.get_logger().info("YOLO detector node started.")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        results = self.model(frame, conf=0.3, imgsz=640, verbose=False)
        result = results[0]

        count = len(result.boxes)

        self.get_logger().info(f"Detected {count} objects.")
        msg_out = String()
        msg_out.data = f"Detected {count} objects."
        self.detection_publisher.publish(msg_out)

def main(args=None):
    rclpy.init(args=args)

    node = YoloDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
