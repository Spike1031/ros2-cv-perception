import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class ImagePublisherNode(Node):
    def __init__(self):
        super().__init__("image_publisher_node")

        self.publisher_ = self.create_publisher(Image, "/image_raw", 10)
        self.bridge = CvBridge()

        self.video_path = "/mnt/c/Users/Spike/cv_projects/ros2-cv-perception/data/input.mp4"
        self.cap = cv2.VideoCapture(self.video_path)

        self.timer = self.create_timer(0.1, self.publish_frame)

        self.get_logger().info("Image publisher node started.")

    def publish_frame(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warn("Video ended. Restarting from first frame.")
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_.publish(msg)

        self.get_logger().info("Published one frame.")

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = ImagePublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
