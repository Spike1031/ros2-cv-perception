# ROS2-Based YOLOv8 Perception Pipeline

This project demonstrates a computer vision perception pipeline for traffic scenes. It includes standalone Python scripts for object detection, object counting, and multi-object tracking, as well as a ROS2-based perception pipeline using image topics and detection result topics.

The project is built around YOLOv8 and OpenCV, and is extended with ROS2 Jazzy to simulate a robotics-style perception workflow.

## Features

* Image object detection with YOLOv8
* Video object detection
* Object counting on images
* Object counting on videos
* Multi-object tracking with ByteTrack
* Output image and video saving
* ROS2 image publishing node
* ROS2 YOLO perception node
* Detection result publishing through ROS2 topics

## Tech Stack

* Python
* OpenCV
* YOLOv8 / Ultralytics
* ByteTrack
* ROS2 Jazzy
* Ubuntu 24.04 / WSL2
* cv_bridge
* sensor_msgs
* std_msgs

## Project Structure

```text
ros2-cv-perception/
├── src/                    # Standalone Python scripts
│   ├── test_yolo_image.py
│   ├── detect_video.py
│   ├── count_objects.py
│   ├── count_video.py
│   └── track_video.py
│
├── data/                   # Input images and videos
├── outputs/                # Detection, counting, and tracking results
├── docs/                   # Demo images and documentation
│
├── ros2_cv_perception/     # ROS2 package for image publishing and YOLO detection
│   ├── cv_perception/
│   │   ├── hello_node.py
│   │   ├── image_publisher_node.py
│   │   └── yolo_detector_node.py
│   ├── package.xml
│   ├── setup.py
│   ├── resource/
│   └── test/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Standalone Python Scripts

The standalone scripts can be used without ROS2. They run object detection, counting, and tracking directly on local image or video files.

### Image Detection

```bash
python src/test_yolo_image.py
```

### Video Detection

```bash
python src/detect_video.py
```

### Image Object Counting

```bash
python src/count_objects.py
```

### Video Object Counting

```bash
python src/count_video.py
```

### Object Tracking

```bash
python src/track_video.py
```

## Output Results

The generated results are saved under:

```text
outputs/
├── image_detection/
├── video_detection/
├── counting_image/
├── counting_video/
└── tracking_video/
```

The output examples include detected bounding boxes, object category labels, confidence scores, object counts, and tracking IDs.

## Demo

### Object Detection

![Object Detection](docs/detection_demo.png)

### Object Counting

![Object Counting](docs/counting_demo.jpg)

### Object Tracking

![Object Tracking](docs/tracking_demo.png)

## ROS2 Perception Pipeline

This project also includes a ROS2-based perception pipeline. The ROS2 part converts a video file into image messages, publishes them to a ROS2 topic, runs YOLOv8 detection in a separate node, and publishes detection results to another topic.

### ROS2 Pipeline Architecture

```text
Video File
    ↓
image_publisher_node
    ↓
/image_raw
    ↓
yolo_detector_node
    ↓
/detections
```

### ROS2 Nodes

#### image_publisher_node

This node reads frames from a local video file using OpenCV and publishes them as ROS2 image messages.

Published topic:

```text
/image_raw
```

Message type:

```text
sensor_msgs/msg/Image
```

#### yolo_detector_node

This node subscribes to `/image_raw`, converts ROS2 image messages back to OpenCV images using `cv_bridge`, runs YOLOv8 inference, and publishes detection count results.

Subscribed topic:

```text
/image_raw
```

Published topic:

```text
/detections
```

Message type:

```text
std_msgs/msg/String
```

Example output:

```text
Detected 8 objects.
Detected 7 objects.
Detected 5 objects.
```

## Running the ROS2 Pipeline

Before running the ROS2 nodes, source the ROS2 workspace:

```bash
source ~/ros2_ws/install/setup.bash
```

### Terminal 1: Start the Image Publisher

```bash
ros2 run cv_perception image_publisher_node
```

### Terminal 2: Start the YOLO Detector

```bash
ros2 run cv_perception yolo_detector_node
```

### Terminal 3: Monitor Detection Results

```bash
ros2 topic echo /detections
```

Expected output:

```text
data: Detected 8 objects.
---
data: Detected 7 objects.
---
data: Detected 5 objects.
---
```

## ROS2 Topics

You can check active topics with:

```bash
ros2 topic list
```

Expected topics include:

```text
/image_raw
/detections
/parameter_events
/rosout
```

You can check the image publishing rate with:

```bash
ros2 topic hz /image_raw
```

## Installation

Install Python dependencies for the standalone scripts:

```bash
pip install -r requirements.txt
```

For the ROS2 part, the project was tested with:

```text
Ubuntu 24.04
ROS2 Jazzy
Python 3.12
```

Required ROS2 packages include:

```bash
sudo apt install -y ros-jazzy-cv-bridge ros-jazzy-vision-opencv
```

Ultralytics YOLO can be installed with:

```bash
pip install ultralytics
```

It is recommended to use a Python virtual environment for installing additional Python packages.

For quick testing on Ubuntu 24.04, `--break-system-packages` was used due to the externally managed Python environment:

```bash
pip install ultralytics --break-system-packages
```

If `cv_bridge` reports a NumPy compatibility issue, use NumPy 1.x:

```bash
pip install "numpy<2" --force-reinstall --break-system-packages
```

## Notes

Large model weights, raw videos, and generated output videos are not tracked in this repository. Files such as `.pt`, `.mp4`, `.avi`, and output folders should be excluded through `.gitignore` to keep the repository lightweight.

Recommended ignored files include:

```text
*.pt
*.mp4
*.avi
outputs/
__pycache__/
```

## Current Status

The current project supports both standalone computer vision scripts and a ROS2-based perception pipeline. The ROS2 pipeline has been tested with a video input, image topic publishing, YOLOv8 inference, and detection result publishing through `/detections`.

## Future Work

* Publish detailed bounding box results instead of only object counts
* Add a ROS2 tracking node
* Publish tracking IDs through a ROS2 topic
* Add a visualization node for annotated images
* Support live camera input when camera access is available
* Add launch files for starting the full pipeline with one command
