from ultralytics import YOLO

model = YOLO("yolov8n.pt")

results = model(
    source = r"C:\Users\Spike\cv_projects\ros2-cv-perception\data\test.jpg",
    save = True,
    project = r"C:\Users\Spike\cv_projects\ros2-cv-perception\outputs",
    name = "image_detection",
    exist_ok = True
)

print("Detection finished.")