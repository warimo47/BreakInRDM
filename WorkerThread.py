import threading
import cv2
import time
import darknet
from datetime import datetime
import random
import struct


class WorkerThread(threading.Thread):
    def __init__(self, _thread_num, _network, _darknet_lock, _class_names, _class_colors,
                 _darknet_width=1920, _darknet_height=1080,
                 _is_sc_server_connect=False, _client_socket=None, _streaming_path="A8_10min.mp4", _cctv_ip=None):
        super().__init__()
        self.thread_num = _thread_num
        self.network = _network
        self.darknet_lock = _darknet_lock
        self.class_names = _class_names
        self.class_colors = _class_colors
        self.darknet_width = _darknet_width
        self.darknet_height = _darknet_height
        self.isSCServerConnect = _is_sc_server_connect
        self.client_socket = _client_socket
        self.streaming_path = _streaming_path
        self.cctvIP = _cctv_ip
        self.cap = None
        self.now_time = None
        self.prev_time = None
        self.diff_time = 1.0
        self.fps = None
        self.ret = None
        self.frame = None
        self.frame_rgb = None
        self.frame_resized = None
        self.img_for_detect = None
        self.detections = None

    def run(self):
        # Load video streaming
        self.cap = cv2.VideoCapture(self.streaming_path)

        self.prev_time = time.time()
        self.diff_time = 1.0

        # cv2.namedWindow(f"TP1 Python")

        while True:
            self.ret, self.frame = self.cap.read()
            self.ret, self.frame = self.cap.read()
            self.ret, self.frame = self.cap.read()
            self.ret, self.frame = self.cap.read()
            self.ret, self.frame = self.cap.read()

            if self.frame is None:
                self.cap = cv2.VideoCapture(self.streaming_path)
                continue
            self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.frame_resized = cv2.resize(self.frame_rgb, (self.darknet_width, self.darknet_height),
                                            interpolation=cv2.INTER_LINEAR)

            self.img_for_detect = darknet.make_image(self.darknet_width, self.darknet_height, 3)
            darknet.copy_image_from_bytes(self.img_for_detect, self.frame_resized.tobytes())

            # Inference
            self.darknet_lock.acquire()
            self.detections = darknet.detect_image(self.network, self.class_names, self.img_for_detect, thresh=0.25)
            self.darknet_lock.release()

            # new_detections = []
            # for label, confidence, bbox in self.detections:
            #     if label == "person":
            #         new_detections.append((label, confidence, bbox))

            # darknet.print_detections(self.detections, True)
            darknet.free_image(self.img_for_detect)

            # Fill packet data
            send_result = -1
            if self.isSCServerConnect is True:
                data_time = f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S.%f')}\0"
                data_obj_num = len(self.detections)

                print(self.cctvIP + "|" + data_time + "|" + str(data_obj_num))

                if_sc100_header = struct.pack("B", 1)  # IF-SC100
                while len(self.cctvIP) < 16:
                    self.cctvIP += "\0"
                if_sc100_ip = self.cctvIP.encode("utf-16le")
                if_sc100_time = data_time.encode("utf-16le")
                if_sc100_obj_num = struct.pack("B", data_obj_num)  # 0 - 40

                send_buffer = if_sc100_header + if_sc100_ip + if_sc100_time + if_sc100_obj_num
                cctv_id = 1
                count = 0

                for label, confidence, bbox in self.detections:
                    left, top, right, bottom = self.get_left_top_right_bottom(bbox)
                    # ID 문자열은 날짜 + CCTV ID + tracking ID로 해주시면 됩니다.
                    data_id = f"{datetime.today().strftime('%Y-%m-%d')} {cctv_id:02d} {count:05d}\0"
                    data_obj_type = random.randrange(0, 3)  # 0=사람, 1=차량, 2=트럭

                    print(f"{count:2d} : {data_id} {data_obj_type} {left} {top} {right} {bottom} {confidence}")

                    if_sc100_id = data_id.encode("utf-16le")
                    if_sc100_obj_type = struct.pack("B", data_obj_type)
                    if_sc100_x_axis = struct.pack("f", 10.0)
                    if_sc100_z_axis = struct.pack("f", 10.0)
                    if_sc100_obj_x1 = struct.pack("i", left)
                    if_sc100_obj_y1 = struct.pack("i", top)
                    if_sc100_obj_x2 = struct.pack("i", right)
                    if_sc100_obj_y2 = struct.pack("i", bottom)
                    if_sc100_percent = struct.pack("f", float(confidence))

                    send_buffer += if_sc100_id + if_sc100_obj_type + if_sc100_x_axis + if_sc100_z_axis
                    send_buffer += if_sc100_obj_x1 + if_sc100_obj_y1 + if_sc100_obj_x2 + if_sc100_obj_y2
                    send_buffer += if_sc100_percent
                    count += 1

                try:
                    send_result = self.client_socket.send(send_buffer)
                except (OSError, BrokenPipeError, ConnectionResetError):
                    self.client_socket.close()
                    is_socket_connect = False
                    while is_socket_connect is False:
                        try:
                            self.client_socket.connect(("192.168.0.107", 6097))
                        except OSError:
                            continue
                        is_socket_connect = True

                if send_result == 0:
                    print(f"{self.thread_num:02d}] Send Error")

            # Drawing
            detections_adjusted = []
            if self.frame is not None:
                for label, confidence, bbox in self.detections:
                    bbox_adjusted = self.convert2original(self.frame, bbox)
                    detections_adjusted.append((str(label), confidence, bbox_adjusted))
            image = darknet.draw_boxes(detections_adjusted, self.frame, self.class_colors)
            cv2.imshow(f"TP1 Python {self.thread_num}", image)
            cv2.waitKey(1)

            self.now_time = time.time()
            self.diff_time = self.now_time - self.prev_time
            self.prev_time = self.now_time
            self.fps = int(1 / self.diff_time)
            sleep_time = 0.20 - self.diff_time
            print(f"{self.thread_num:02d}] FPS : {self.fps:02d} send_result : {send_result} "
                  f"diff_time : {self.diff_time:0.6f} sleepTime : {sleep_time:0.6f}")

            if sleep_time > 0.18:
                time.sleep(sleep_time)

            # cv2.waitKey(200 - int(self.diff_time * 1000.0))

        self.cap.release()

    def convert2original(self, _image, _bounding_box):
        x, y, w, h = _bounding_box
        _height = self.darknet_height
        _width = self.darknet_width
        x, y, w, h = x / _width, y / _height, w / _width, h / _height

        image_h, image_w, __ = _image.shape

        orig_x = int(x * image_w)
        orig_y = int(y * image_h)
        orig_width = int(w * image_w)
        orig_height = int(h * image_h)

        bbox_converted = (orig_x, orig_y, orig_width, orig_height)

        return bbox_converted

    def get_left_top_right_bottom(self, _bounding_box):
        x, y, w, h = _bounding_box
        x, y, w, h = x / self.darknet_width, y / self.darknet_height, w / self.darknet_width, h / self.darknet_height
        ret = (int(x * 1920), int(y * 1080), int(x * 1920 + w * 1920), int(y * 1080 + h * 1080))
        return ret
