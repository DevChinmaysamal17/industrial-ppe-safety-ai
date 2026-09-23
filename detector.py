from ultralytics import YOLO

class PPEDetector:
    def __init__(self, model_path="models/ppe_yolov8.pt"):
        self.model = YOLO(model_path)

    def predict(self, frame, conf=0.4):
        results = self.model.predict(frame, conf=conf, verbose=False)
        return results[0]