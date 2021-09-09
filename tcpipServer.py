import socket


if __name__ == '__main__':
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("", 6097))
    listen_socket.listen(0)

    print("Listen start")

    client_socket, address = listen_socket.accept()  # 연결 요청을 수락함. 그러면 아이피주소, 포트등 데이터를 반환

    print(f"{address} is connect")

    while True:
        data = client_socket.recv(4096)  # 클라이언트로 부터 데이터를 받음. 출력되는 버퍼 사이즈. (만약 2할 경우, 2개의 데이터만 전송됨)
        if len(data) == 0:
            break
        print("받은 데이터:", data.decode())  # 받은 데이터를 해석함.

    print("Program end")
