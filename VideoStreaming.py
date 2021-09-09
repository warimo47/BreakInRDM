import cv2


if __name__ == '__main__':
    cap = cv2.VideoCapture("rtsp://192.168.0.60:554/0")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video streaming', frame)

        if cv2.waitKey(1) == 27:
            break
    cap.release()
