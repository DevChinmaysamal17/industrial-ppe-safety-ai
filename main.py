import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from detector import PPEDetector

app = FastAPI()
detector = PPEDetector()

VIDEO_SOURCE = "video/sample_video.mp4"


def gen_frames(source):
    # source: 0 (int) for webcam, or a file path string for prerecorded video
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        return

    is_webcam = isinstance(source, int)

    while True:
        ret, frame = cap.read()
        if not ret:
            if is_webcam:
                break
            # loop the prerecorded video instead of stopping
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        result = detector.predict(frame)
        annotated = result.plot()
        _, buffer = cv2.imencode(".jpg", annotated)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    cap.release()


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html") as f:
        return f.read()


@app.get("/video_feed")
def video_feed(mode: str = "video"):
    # mode=video -> prerecorded file, mode=webcam -> live camera
    source = 0 if mode == "webcam" else VIDEO_SOURCE
    return StreamingResponse(gen_frames(source), media_type="multipart/x-mixed-replace; boundary=frame")


app.mount("/static", StaticFiles(directory="static"), name="static")