import os
import shutil
import cv2
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from detector import PPEDetector

app = FastAPI()
detector = PPEDetector()

VIDEO_DIR = "video"
os.makedirs(VIDEO_DIR, exist_ok=True)

ALLOWED_EXT = {".mp4", ".mov", ".avi", ".mkv"}


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


@app.get("/videos")
def list_videos():
    """List available prerecorded videos in the video/ directory."""
    files = [
        f for f in os.listdir(VIDEO_DIR)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXT
    ]
    return {"videos": sorted(files)}


@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return JSONResponse({"error": "Unsupported file type"}, status_code=400)

    dest_path = os.path.join(VIDEO_DIR, file.filename)
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    return {"filename": file.filename}


@app.get("/video_feed")
def video_feed(mode: str = "webcam", filename: str = ""):
    # mode=webcam -> live camera, mode=video -> prerecorded file (needs filename)
    if mode == "video":
        if not filename:
            return JSONResponse({"error": "No filename provided"}, status_code=400)
        source = os.path.join(VIDEO_DIR, filename)
        if not os.path.isfile(source):
            return JSONResponse({"error": "File not found"}, status_code=404)
    else:
        source = 0

    return StreamingResponse(gen_frames(source), media_type="multipart/x-mixed-replace; boundary=frame")


app.mount("/static", StaticFiles(directory="static"), name="static")