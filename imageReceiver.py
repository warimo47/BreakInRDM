import socket
import struct
import cv2
import numpy
import datetime

# socket 수신 버퍼를 읽어서 반환하는 함수
def receive_all(sock, count):
    buf = b''
    while count:
        new_buf = sock.recv(count)
        if not new_buf:
            return None
        buf += new_buf
        count -= len(new_buf)
    return buf


if __name__ == '__main__':
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("", 6097))
    listen_socket.listen(0)

    print("Listen start")

    client_socket, address = listen_socket.accept()  # 연결 요청을 수락함. 그러면 아이피주소, 포트등 데이터를 반환

    print(f"{address} is connect")

    image = numpy.zeros((1080, 1920, 3), numpy.uint8)
    while True:
        image_length_b = client_socket.recv(4)  # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
        if len(image_length_b) == 0:
            break
        image_length = struct.unpack("i", image_length_b)

        print(f"{datetime.datetime.now()} {image_length[0]}")
        # 이미지를 수신받아서 이미지로 변환 하고 화면에 출력
        string_data = receive_all(client_socket, image_length[0])

        image_data = numpy.fromstring(string=string_data, dtype='uint8')
        decode_img = cv2.imdecode(image_data, 1)
        cv2.imshow("Image Receiver", decode_img)
        if cv2.waitKey(1) == ord("q"):
            break
    print("Program end")
