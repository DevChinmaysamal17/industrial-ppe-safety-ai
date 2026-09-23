import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera failed to open")
else:
    ret, frame = cap.read()
    print("Frame captured:", ret)
    cv2.imshow("test", frame)
    cv2.waitKey(3000)
cap.release()
cv2.destroyAllWindows()