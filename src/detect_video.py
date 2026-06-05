from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.predict(
    source=r"C:\Users\Spike\cv_projects\ros2-cv-perception\data\input.mp4",
    save=True,
    project=r"C:\Users\Spike\cv_projects\ros2-cv-perception\outputs",
    name="video_detection",
    exist_ok=True,
    conf=0.3,
    imgsz=640,
    vid_stride=5
)

print("Video detection finished.")