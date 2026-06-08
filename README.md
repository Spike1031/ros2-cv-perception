# ROS2-Based YOLOv8 Perception Pipeline

This project demonstrates a computer vision pipeline for traffic scene perception, including object detection, object counting, and multi-object tracking using YOLOv8 and ByteTrack.

## Features

- Image object detection
- Video object detection
- Object counting on images
- Object counting on videos
- Output image and video saving
- Object tracking with ByteTrack
- ROS2 image publishing pipeline
- ROS2 YOLO perception node

## Tech Stack

- Python
- OpenCV
- YOLOv8
- Ultralytics
- ByteTrack

## Project Structure

```text
ros2-cv-perception/
├── src/
├── data/
├── outputs/
└── docs/
```

## How to Run

Image detection:

```bash
python src/test_yolo_image.py
```

Video detection:

```bash
python src/detect_video.py
```

Image counting:

```bash
python src/count_objects.py
```

Video counting:

```bash
python src/count_video.py
```

Object tracking:

```bash
python src/track_video.py
```

## Results

The output results are saved in:

```text
outputs/
├── image_detection/
├── video_detection/
├── counting_image/
├── counting_video/
└── tracking_video/
```

## Demo

### Object Detection

![Detection](docs/detection_demo.png)

### Object Counting

![Counting](docs/counting_demo.jpg)

### Object tracking

![tracking](docs/tracking_demo.png)

## ROS2 Perception Pipeline

This project also includes a ROS2-based perception pipeline built on Ubuntu 24.04 and ROS2 Jazzy.

### Pipeline Architecture

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

### Components

#### image_publisher_node

Publishes video frames to the ROS2 topic:

```text
/image_raw
```

#### yolo_detector_node

Subscribes to:

```text
/image_raw
```

Runs YOLOv8 inference and publishes detection results to:

```text
/detections
```

#### detections topic

Example output:

```text
Detected 8 objects.
Detected 7 objects.
Detected 5 objects.
```

### ROS2 Commands

Start image publisher:

```bash
ros2 run cv_perception image_publisher_node
```

Start YOLO detector:

```bash
ros2 run cv_perception yolo_detector_node
```

Monitor detection results:

```bash
ros2 topic echo /detections
```

### Technologies

* ROS2 Jazzy
* Ubuntu 24.04 (WSL2)
* Python
* OpenCV
* YOLOv8
* cv_bridge
* sensor_msgs
* ROS2 Topics
