import rclpy
from rclpy.node import Node


class HelloNode(Node):
    def __init__(self):
        super().__init__("hello_node")
        self.get_logger().info("Hello from cv_perception package!")


def main(args=None):
    rclpy.init(args=args)
    node = HelloNode()
    rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
