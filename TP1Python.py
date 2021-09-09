import threading

import cv2
import darknet
import socket
import random
import WorkerThread


if __name__ == '__main__':
    # Load yolo network
    network, class_names, class_colors = darknet.load_network(
        config_file="./20210322_yolov3.cfg",
        data_file="./20210322_obj.data",
        weights="./20210322_yolov3_final.weights",
        # config_file="./COCOyolov3.cfg",
        # data_file="./COCOyolov3.data",
        # weights="./COCOyolov3.weights",
        batch_size=1
        )
    darknet_lock = threading.Lock()
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    # print(f"darknet_width : {darknet_width} darknet_height : {darknet_height}")
    cctvIPList = ["192.168.0.60", "192.168.0.61"]
    # videoStreamingPathList = ["rtsp://admin:admin@192.168.0.60:554/0"]
    videoStreamingPathList = ["A8Sample.mp4", "A8Sample.mp4"]

    # Initialize network object
    client_socket = None
    isSCServerConnect = True
    tm = None
    if isSCServerConnect is True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("192.168.0.107", 6097))

    random.seed(3)  # deterministic bbox colors

    threads = []
    for i in range(len(videoStreamingPathList)):
        threads.append(WorkerThread.WorkerThread(
            _thread_num=i,
            _network=network,
            _darknet_lock=darknet_lock,
            _class_names=class_names,
            _class_colors=class_colors,
            _darknet_width=darknet_width,
            _darknet_height=darknet_height,
            _is_sc_server_connect=isSCServerConnect,
            _client_socket=client_socket,
            _streaming_path=videoStreamingPathList[i],
            _cctv_ip=cctvIPList[i])
        )

    for th in threads:
        th.start()

    '''
    while True:
        if cv2.waitKey(100) == 27:
            isThreadStop = True
            break
    '''

    for th in threads:
        th.join()

    cv2.destroyAllWindows()
