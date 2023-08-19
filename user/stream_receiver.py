"""receive frames from the sender and calculate the bandwidth of the stream"""
import subprocess as sp
import numpy as np
import cv2
import  time
from pathlib import Path 

# 1. 串联ffmpeg实现计算带宽

# 2. 用socket连接实现获取带宽
class FFmpegReceiver:
    def __init__(self, stream_ip):
        self.ip = stream_ip
        self.rtspUrl = 'rtsp://%s:%d/mystream' % (self.ip, 8554)
        self.fps =25
        self.command = [
            'ffmpeg',
            '-f', 'rtsp',  # 强制输入或输出文件格式
            '-rtsp_transport', 'tcp',  # 强制使用 tcp 通信
            '-timeout', '10',  # 设置TCP连接的等待时间
            '-i', self.rtspUrl,  # 输入
            '-f','rawvideo', # 以为rawvideo格式输出
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            # '-video_size', '256x256',  # 设置图像尺寸
            '-preset', 'ultrafast',
            '-r', '10',  # 设置帧率
            # '-an', '-', # output no audio
            'pipe:1'
            ]
        
        self.command2 = [
            'ffmpeg',
            '-i','pipe:1',
            '-c:v','copy', # 直接copy 视频流，不对视频进行编码
            'f', 'rawvideo',  # 强制输入或输出文件格式
            # '-f', 'image2pipe',  # 强制输出到管道
            'pipe:2'
        ]

        self.pipe = sp.Popen(self.command, stdout=sp.PIPE)
        self.pipe2 = sp.Popen(self.command2, 
                              stdin=self.pipe.stdout,
                              stdout=sp.PIPE)
    def read(self): # 不用该自定义方法，用cv2库读取
        frame = self.pipe.stdout.read(256*256*3)
        if frame is not None:
            frame = np.frombuffer(frame, dtype='uint8')
            return frame.reshape((256, 256, 3))
        else:
            return None

    def receive(self):
        count = 0
        while True:
            frame = self.read()
            if frame is not None:
                print("No. %d: " % count, np.mean(frame))
                count += 1
                if Path('temp').exists() is False:
                    Path('temp').mkdir(parents=True, exist_ok=True)
                cv2.imwrite('temp/%d.jpeg' % count, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            self.pipe.stdout.flush()

    def h264Bandwidth(self,unit=1024):
        while True:
            # print(1)
            time_start = time.time()
            out = self.pipe2.stdout.read(unit)
            if out==b'':
                continue 
            time_end = time.time()
            time_duration = time_end - time_start  
            bit_rate = unit*8/time_duration/1024
            print(f'bit_rate:{bit_rate}kbps')



if __name__ == '__main__':
    streamer = FFmpegReceiver('192.168.31.17')
    # streamer.receive()
    streamer.h264Bandwidth()