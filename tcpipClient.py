import socket
import time

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('222.99.97.171', 12348))  # 접속할 서버의 ip 주소와 포트번호를 입력.

    index = 0
    while True:
        index += 1
        client_socket.send(f'Hello {index}'.encode())  # 내가 전송할 데이터를 보냄.
        print(f"{index:05d} send")
        time.sleep(1.0)
