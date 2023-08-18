import cv2
from PIL import Image,ImageTk
import tkinter
from tkinter import messagebox
import numpy as np 
import time
import sys
from threading import Thread
from pathlib import Path
import subprocess
import socket 
import re
from multiprocessing import Process
import os 
from vidgear.gears import CamGear
from rtscapture import RTSCapture
# Meta
native_ip = socket.gethostbyname(socket.gethostname())
flag = 0 #关闭拉流
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
frame_rate = 0
root_dir = Path(os.getcwd()) # cam_broadcast目录

video = None
video_fps = 0.
video_bit_rate = 0.
entry_string = ''
rtsp_server_url = ''
font_setting = ('Arial', 15)
# Function
def get_entry_string():
    global rtsp_server_url
    global entry_string 
    entry_string = input_entry.get()
    
    rtsp_server_url = f'rtsp://{entry_string}/mystream'
    # hint_label.configure(text=entry_string)
    return entry_string 



# todo

# 两个按钮，连接，断开
# button function
def connect():
    global flag 
    global rtsp_server_url
    global video

    get_entry_string()
    print(f'即将要连接的推流端地址为：{rtsp_server_url}')
    try:
        # video = cv2.VideoCapture(rtsp_server_url)
        # video = CamGear(source=rtsp_server_url).start()
        print('testing 1')
        video = RTSCapture.create(rtsp_server_url)

        print('testting 2')

        flag = 1
        print('连接成功')
        button_start['state']='disabled'
        button_play['state']='normal'
        button_close['state']='normal'
    except Exception as e:
        print(e)
        messagebox.showerror('错误','请先打开发送端，或者请检查IP:PORT是否正确')


def close():
    global flag 
    global video
    # video.release()
    
    # rtscapture
    if video.isOpened():
        print(f'释放video')
        video.stop_read() # stop rtpcapture read thread
        video.release()
    # camgear
    # video.stop()
    flag = 0
    print('关闭成功')
    # 清空stdout
    del video
    sys.stdout.flush()
    sys.stderr.flush()
    button_start['state']='normal'
    button_play['state']='disabled'
    button_close['state']='disabled'
# 拼接rtsp_server_url

# 启动拉流 播放视频
def imshow():
    global video
    global root
    global image
    global video_fps
    global video_bit_rate
    try:
        res ,img = video.read() # 容易出错,video.release()后，再次调用read()会报错
        if  res==True and flag ==1:
            # get meta
            video_fps = video.get(cv2.CAP_PROP_FPS)
            video_bit_rate = video.get(cv2.CAP_PROP_BITRATE)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = ImageTk.PhotoImage(img)
            image.image=img
            image['image']=img
            delay_label.config(text=f'帧率:{video_fps}')
            bit_rate_label.config(text=f'码率:{video_bit_rate}')
            root.after(10,imshow)
        else:
            print('发送端已关闭')
            image.config(text='发送端已关闭')
            return 0
    except Exception as e:
        print('推送端未开启或已关闭')
    # res,img=video.read()

# 断开，video.release() , 

def show_video():
    global video
    global flag
    if flag ==1:
        video.start_read()  # rtscapture
        imshow()
  
        # button state
        button_start['state'] = 'disabled'
        button_play['state'] = 'disabled'
        button_close['state'] = 'normal'
    else:
        messagebox.showerror('错误','请先打开发送端，或者检查网络连接')

# Settings Variable
root = tkinter.Tk()
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.title('接受端')

# 输入框 + 按钮，输入框手动输入ip地址和端口号，按钮用于连接
input_label = tkinter.Label(root,text= '推送端 IP:PORT',font=font_setting)
input_entry = tkinter.Entry(root, width=30, textvariable=tkinter.StringVar(value=f'{native_ip}:8554'),font=font_setting)
button_start = tkinter.Button(root, height=1,text='连接',command=connect,font=('Arial', 13))
button_play = tkinter.Button(root, height=1,text='播放',command=show_video,font=('Arial', 13),state='disabled')
button_close = tkinter.Button(root,height=1, text='断开',command=close,font=('Arial',13),state='disabled')
# hint_label = tkinter.Label(root,text='',font=font_setting)

# 位置 # 共1行 5列
input_label.grid(row=0, column=0,columnspan=1 ,sticky=tkinter.N+tkinter.W,padx=5,pady=8)
input_entry.grid(row=0, column=1,columnspan=2 ,sticky=tkinter.N+tkinter.W, padx=5,pady=8)
button_start.grid(row=0,column=3,columnspan=1,sticky=tkinter.N+tkinter.W, padx=5,pady=5)
button_play.grid(row=0,column=4,columnspan=1,sticky=tkinter.N+tkinter.W, padx=5,pady=5)
button_close.grid(row=0,column=5,columnspan=1,sticky=tkinter.N+tkinter.W, padx=5,pady=5)
# hint_label.grid(row=0, column=6,columnspan=1  ,sticky=tkinter.N+tkinter.W, padx=5,pady=8)

# 参数列
delay_label = tkinter.Label(root,text='延迟:',font=font_setting)
bit_rate_label = tkinter.Label(root,text='码率:',font=font_setting)

# 位置 共两行一列
delay_label.grid(row=1,column=0,columnspan=1,sticky= tkinter.N+tkinter.W,padx=5,pady=5)
bit_rate_label.grid(row=2,column=0,columnspan=1,sticky= tkinter.N+tkinter.W,padx=5,pady=5)


    
#     #创建label显示视频
image = tkinter.Label(root, 
                    #   width=VIDEO_WIDTH, 
                    #   height=VIDEO_HEIGHT,
                    text='视频显示区域')
image.grid(row=1, column=1,rowspan=3,columnspan=6, sticky=tkinter.N+tkinter.W)


if __name__ == '__main__':

    root.mainloop()
    root.quit()

