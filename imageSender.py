import socket
import time
import cv2
import struct
import numpy

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    video_capture = cv2.VideoCapture("rtsp://admin:admin@192.168.0.60:554/0")

    # client_socket.connect(('222.99.97.171', 12348))
    client_socket.connect(("192.168.0.119", 6097))

    sending_index = 0

    print("loop start")
    while True:
        for i in range(6):
            ret, frame = video_capture.read()

        # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, img_encode = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(img_encode)
        stringData = data.tostring()
        # stringData = frame.tostring()

        # 이미지 데이터 길이 전송
        image_length = len(stringData)
        client_socket.send(struct.pack("i", image_length))

        # String 형태로 변환한 이미지를 socket 을 통해서 전송
        client_socket.send(stringData)
