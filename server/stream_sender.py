
"""H.264 Streaming methods"""
import numpy as np
import subprocess as sp
import time
import cv2
# from imageio import get_reader
import queue
from threading import Thread
from config import rtsp_server_url
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
                # print('Video not available.')
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
    def __init__(self, fps=25, frame_size=(640,480),logging=False):
        self.frame_generator = FrameGenerator((640,480, 3), source=0)
        self.fps = fps
        self.frame_size = frame_size
        self.size_str = '%dx%d' % (self.frame_size[0], self.frame_size[1])
        self.rtspUrl =rtsp_server_url
        # written according to https://www.cnblogs.com/Manuel/p/15006727.html

        self.command = [
            'ffmpeg',
            # 're',#
            # '-y', # 无需询问即可覆盖输出文件
            '-f', 'rawvideo',  # 强制输入或输出文件格式
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-s', self.size_str,  # 设置图像大小
            '-r', str(fps),  # 设置帧率
            '-i', '-',  # 输入
            '-timeout', '10',  # 设置TCP连接的等待时间

            '-c:v', 'libx265',
            # '-x264opts', 'bitrate=%d' % self.rate,  # 设置比特率（kbps）
            '-pix_fmt', 'bgr24',
            '-preset', 'ultrafast',
            '-f', 'rtsp',  # 强制输入或输出文件格式
            # '-rtsp_transport', 'udp',  # 使用UDP推流
            '-rtsp_transport', 'tcp',  # 使用TCP推流

            '-f','tee', # 复制输出
            '-map','0:v', # 选择第0个输入的视频流
            f'[f=rtsp]{self.rtspUrl}|[f=hevc]pipe:1', # 两个输出
]
        if logging == False:
            self.command.extend(['-loglevel', 'quiet'])
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
    
def get_bit_rate():
    global q
    while True:
        start_time = time.time()
        content = 1024 # 1 KB
        out = streamer.pipe.stdout.read(content) # 固定读取 1KB 
        end_time = time.time()
        duration = end_time - start_time
        if out == b'':continue
        if duration != 0:bit_rate = 8*content / (duration*1000) # 转为kbps 
        if bit_rate >500 and bit_rate < 6000: # 更严谨做法是计算一段时间平均值
            try:
                q.put_nowait(bit_rate)
            except queue.Full:
                q.get()
                q.put_nowait(bit_rate)
            # print('%.2f kbps'%bit_rate)
def show_bit_rate():
    global q
    while True:
        if not q.empty():
            bit_rate = q.get()
            # print('%.2f kbps'%bit_rate)
            time.sleep(0.5)

if __name__ == '__main__':
    q =queue.Queue(50)
    streamer = FFmpegStreamer(fps=30,logging=True) #这里的也是GUI上的内容
    Thread(target=streamer.push_stream).start()
    Thread(get_bit_rate).start()
    Thread(show_bit_rate).start()
    print('启动推送端')