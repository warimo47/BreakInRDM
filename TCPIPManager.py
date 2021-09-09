import socket
import struct
import random
from datetime import datetime
import cv2


class TCPIPManager:
    def __init__(self, ip_str="192.168.0.107", port_num=6097):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip_str, port_num))

    def send(self):
        data_ip = "192.168.0.70"
        # 시간 문자열은 예제와 같은 (yyyy-MM-dd HH:mm:ss.ffffff) 포맷으로 해주시면 됩니다.
        data_time = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')}\0"
        data_obj_num = random.randrange(1, 41)

        # print(data_ip + " " + data_time + " " + str(data_obj_num))

        if_sc100_header = struct.pack("B", 1)  # IF-SC100
        while len(data_ip) < 16:
            data_ip += "\0"
        if_sc100_ip = data_ip.encode("utf-16le")
        if_sc100_time = data_time.encode("utf-16le")
        if_sc100_obj_num = struct.pack("B", data_obj_num)  # 0 - 40

        send_buffer = if_sc100_header + if_sc100_ip + if_sc100_time + if_sc100_obj_num
        cctv_id = 1

        for i in range(data_obj_num):
            # ID 문자열은 날짜 + CCTV ID + tracking ID로 해주시면 됩니다.
            data_id = f"{datetime.today().strftime('%Y-%m-%d')} {cctv_id:02d} {i:05d}\0"
            data_obj_type = random.randrange(0, 3)  # 0=사람, 1=차량, 2=트럭
            rand_obj_x = random.randrange(100, 1820)
            rand_obj_y = random.randrange(100, 980)
            data_percent = random.uniform(0, 100)
            data_action = random.randrange(0, 5)  # 0=정상상태, 1=쓰러짐, 2=월담, 3=싸움, 4=밀수
            # 0=빨강, 1=주황, 2=노랑, 3=연두, 4=초록, 5=청록, 6=파랑, 7=남색,
            # 8=보라, 9=자주, 10=분홍, 11=갈색, 12=하양, 13=회색, 14=검정
            data_color = random.randrange(0, 15)
            data_red = random.randrange(0, 256)
            data_green = random.randrange(0, 256)
            data_blue = random.randrange(0, 256)

            log = f"{i} : {data_id} {data_obj_type} "
            log += f"{rand_obj_x - 100} {rand_obj_y - 100} {rand_obj_x + 100} {rand_obj_y + 100} {data_percent}"
            log += f"{data_action} {data_color} {data_red} {data_green} {data_blue}"
            print(log)

            if_sc100_id = data_id.encode("utf-16le")
            if_sc100_obj_type = struct.pack("B", data_obj_type)
            if_sc100_x_axis = struct.pack("f", 10.0)
            if_sc100_z_axis = struct.pack("f", 10.0)
            if_sc100_obj_x1 = struct.pack("i", rand_obj_x - 100)
            if_sc100_obj_y1 = struct.pack("i", rand_obj_y - 100)
            if_sc100_obj_x2 = struct.pack("i", rand_obj_x + 100)
            if_sc100_obj_y2 = struct.pack("i", rand_obj_y + 100)
            if_sc100_percent = struct.pack("f", data_percent)

            send_buffer += if_sc100_id + if_sc100_obj_type + if_sc100_x_axis + if_sc100_z_axis
            send_buffer += if_sc100_obj_x1 + if_sc100_obj_y1 + if_sc100_obj_x2 + if_sc100_obj_y2 + if_sc100_percent

        send_ret = self.client_socket.send(send_buffer)
        print(send_ret)
        return send_ret


if __name__ == '__main__':
    myTM = TCPIPManager()
    while True:
        # print("연결중")
        cv2.waitKey(200)
        myTM.send()
