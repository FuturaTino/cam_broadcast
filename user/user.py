import cv2
import numpy as np 
from vidgear.gears import CamGear
from rtscapture import RTSCapture
import sys
sys.path.append('..')
from server.config import rtsp_server_url,rtp_server_url
# 根据rtsp服务器来接受画面

# 读取视频流
# cap = CamGear(source=rtp_server_url).start()
cap = RTSCapture.create(rtp_server_url)
# cap.start_read()
def pull_stream():
    """
    yield frame
    """
    while True:
        try:
            _,frame = cap.read()
        except:
            # 构建一个黑色的 640x480 图像
            frame = np.zeros((480, 640, 3), np.uint8)
            # 画一条 5px 宽的蓝色对角线
            cv2.line(frame, (0, 0), (640, 480), (255, 0, 0), 5)
        yield frame
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    for frame in pull_stream():
        cv2.imshow('user end',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()