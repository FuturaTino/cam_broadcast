
"""H.264 Streaming methods"""
import numpy as np
import subprocess as sp
import time
import cv2
# from imageio import get_reader
import queue
from threading import Thread
class FrameGenerator:
    """
generate a frame of random gray scale
    """

    def __init__(self, size, source=None):
        self.size = size
        self.count = 0
        self.source = source
        if self.source is not None:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                print('Video not available.')
                self.source = None

    def generate(self):
        """
    generate a frame from camera or as a gray scale
        :return:
        """
        frame_gray = np.random.randint(0, 255) * np.ones(self.size).astype('uint8')
        if self.source is None:
            return frame_gray
        else:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                self.cap = cv2.VideoCapture(self.source)
                return self.generate()


class FFmpegStreamer:
    def __init__(self, target_ip, target_port=8554, fps=25, frame_size=(640,480), rate=20):
        self.frame_generator = FrameGenerator((640,480, 3), source=0)
        self.target_ip = target_ip
        self.target_port = target_port
        self.fps = fps
        self.frame_size = frame_size
        self.size_str = '%dx%d' % (self.frame_size[0], self.frame_size[1])
        self.rate = rate  # kbps
        self.rtspUrl = 'rtsp://%s:%d/mystream' % (self.target_ip, self.target_port)
        # written according to https://www.cnblogs.com/Manuel/p/15006727.html
        self.queue = queue.Queue(maxsize=50)
        self.command = [
            'ffmpeg',
            '-f', 'rawvideo',  # 强制输入或输出文件格式
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-s', self.size_str,  # 设置图像大小
            '-r', str(fps),  # 设置帧率
            '-i', '-',  # 输入
            '-timeout', '10',  # 设置TCP连接的等待时间
            # '-b:v', '%dk' % self.rate,  # 设置数据率
            '-c:v', 'libx264',
            '-pix_fmt', 'bgr24',
            '-preset', 'ultrafast',
            '-rtsp_transport', 'tcp',  # 使用TCP推流
            '-loglevel', 'quiet',  # 设置日志级别
            '-f','tee', # 复制输出
            '-map','0:v', # 选择第0个输入的视频流
            f'[f=rtsp]{self.rtspUrl}|[f=hevc]pipe:1', # 两个输出
]
# 成功        
    
        self.pipe = sp.Popen(self.command, 
                             stdin=sp.PIPE,
                             stdout=sp.PIPE,
                            #  bufsize=1024**3
                             )
        self.count = 0

    def set_rate(self, rate):
        self.rate = rate
        self.command[10] = '%dk' % self.rate
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)

    def push_stream(self):
        while True:
            frame = self.frame_generator.generate()
            self.pipe.stdin.write(frame.tobytes())
            # print('No. %d: ' % self.count, np.mean(frame))
    
    def get_bit_rate(self):
        while True:
            start_time = time.time()
            content = 1024 # 1 KB
            out = self.pipe.stdout.read(content) # 固定读取 1KB 
            end_time = time.time()
            duration = end_time - start_time
            if out == b'':
                continue
            if duration != 0:
                bit_rate = 8*content / (duration*1000) # 转为kbps 

            
            if bit_rate >500 and bit_rate < 6000: # 更严谨做法是计算一段时间平均值
                try:
                    self.queue.put_nowait(bit_rate)
                except queue.Full:
                    self.queue.get()
                    self.queue.put_nowait(bit_rate)
                # print('%.2f kbps'%bit_rate)
    def show_rate(self):
        while True:
            if not self.queue.empty():
                bit_rate = self.queue.get()
                print('%.2f kbps'%bit_rate)
                time.sleep(0.5)

if __name__ == '__main__':
    streamer = FFmpegStreamer('192.168.31.17', fps=30, rate=5)
    Thread(target=streamer.push_stream).start()
    Thread(target=streamer.get_bit_rate).start()
    Thread(target=streamer.show_rate).start()
    print('启动推送端')