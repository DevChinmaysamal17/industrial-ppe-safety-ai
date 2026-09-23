import cv2
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, HTMLResponse
from detector import PPEDetector
import numpy as np

app = FastAPI()
detector = PPEDetector()

def gen_frames(source=0):
    cap = cv2.VideoCapture(source)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = detector.predict(frame)
        annotated = result.plot()
        _, buffer = cv2.imencode(".jpg", annotated)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
    cap.release()

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html><body>
        <h2>PFE (PPE) Detection Live Feed</h2>
        <img src="/video_feed" width="800">
    </body></html>
    """

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(0), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/detect_image")
async def detect_image(file: UploadFile = File(...)):
    contents = await file.read()
    npimg = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    result = detector.predict(frame)
    detections = [
        {"class": detector.model.names[int(b.cls)], "conf": float(b.conf)}
        for b in result.boxes
    ]
    return {"detections": detections}