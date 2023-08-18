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
import re
from multiprocessing import Process
from utils_server import push_stream
import os 
from rtscapture import RTSCapture

from rtscapture import RTSCapture
from config import rtsp_server_url

# Meta
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
frame_rate = 0
root_dir = Path(os.getcwd()) # server目录
flag = 0 #关闭推流
# Variable
video = None
thread_for_pull_stream  = None 
process_for_rtsp_server = None
thread_for_push_stream = None
process_for_push_stream = None


# funciton
def output_video_msg(pipe:subprocess.PIPE):
    global flag
    meta_dict = {}
    print(type(flag))
    # pipe 就是 process.stdout
    while True:
        if flag == 0:
            break 
        # print(1)
        line = pipe.readline()
        if line.startswith('frame'):
            meta = line.split('=')
            # print(meta)
            try:
                meta_dict = {
                    'frame':meta[1].split(' ')[-2],
                    'frame_rate':meta[2].split(' ')[-2],
                    'qp':meta[3].split(' ')[0],
                    'size':meta[4].split(' ')[0],
                    'time':meta[5].split(' ')[0],
                    'bit_rate':meta[6].split(' ')[0],
                    'speed': meta[7]
                }
            except Exception as e:
                print(e)
                print(meta)
                # after 1w frame
                if meta[0].startswith('frame='):
                    meta_dict = {
                        'frame':meta[0].split('=')[-1],
                        'frame_rate':meta[2],
                        'qp':meta[3],
                        'size':meta[4].split('=')[-1],
                        'time':meta[5].split('=')[-1],
                        'bit_rate':meta[6].split('=')[-1],
                        'speed': meta[7].split('=')[-1]
                    }
                else:
                    print(f'len(meta): {len(meta)}')
                    print(f'meta[1]:{meta[1]}')
                    print(f'meta[3]:{meta[3]}')
                    print(f'meta[4]: %s'% meta[4].split('=')[-1])
                    print(f'meta[5]: %s'% meta[5].split('=')[-1])
                    print(f'meta[6]: %s'% meta[6].split('=')[-1])                
                    print(f'meta[7]: %s'% meta[7].split('=')[-1])
                    meta_dict = {
                        'frame':'N/A',
                        'frame_rate':meta[3],
                        'qp':'N/A',
                        'size':meta[5].split('=')[-1],
                        'time':meta[6].split('=')[-1],
                        'bit_rate':meta[7].split('=')[-1],
                        'speed': 'N/A'
                    }


            frame_label.configure(text=f'总帧数: %s'% meta_dict['frame'])
            frame_rate_label.configure(text=f'帧率: %s'% meta_dict['frame_rate'])
            qp_label.configure(text=f'量化参数: %s'% meta_dict['qp'])
            size_label.configure(text=f'有效载荷: %s'% meta_dict['size'])
            time_label.configure(text=f'时间: %s'% meta_dict['time'])
            bit_rate_label.configure(text=f'比特率: %s'% meta_dict['bit_rate'])
            speed_label.configure(text=f'编码速度: %s'% meta_dict['speed'])

    return 0 
    
def start_push_stream():
    # Start rtsp server for rtp pack and push stream , and start thread for push stream
    # global thread_for_push_stream
    global video 
    global flag 
    global process_for_push_stream
    global process_for_rtsp_server
    print(f'进入目录:{os.getcwd()}')
    os.chdir(root_dir / 'mediamtx')
    process_for_rtsp_server = subprocess.Popen(['mediamtx.exe'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(0.5)
    os.chdir(root_dir)
    print(f'进入目录2:{os.getcwd()}')
    process_for_push_stream = subprocess.Popen(['utils_server.exe'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
 
    flag = 1
    # Print video message
    Thread(target=output_video_msg,daemon=True,args=(process_for_push_stream.stderr,)).start()
    time.sleep(0.5)
    # update_fps() # update when flag ==1
    print(f'rtsp server pid : {process_for_rtsp_server.pid}')
    print(f'cam and push stream pid : {process_for_push_stream.pid}')
    button_start['state'] = 'disabled'
    button_show['state'] = 'normal'
    button_close['state'] = 'normal'  
    return 0 
    pass

def close_push_stream():
    global flag 
    global process_for_push_stream
    global process_for_rtsp_server
    try:
        flag = 0
        # 1. 释放video 2.关闭所有进程 3.释放stdout stderr 
        if video is not None:
            # cv2
            # video.release()

            # rtscapture
            video.stop_read()
        print(f'flag={flag}')
        # process_for_push_stream.kill()
        # process_for_rtsp_server.kill()
        os.system('taskkill /f /im %s' % 'ffmpeg.exe')
        # kill second utils_server.exe
        os.system('taskkill /f /im %s' % 'utils_server.exe')
        os.system('taskkill /f /im %s' % 'mediamtx.exe')
        process_for_push_stream = None
        process_for_rtsp_server = None

        button_start['state'] = 'normal'
        button_show['state'] = 'disabled'
        button_close['state'] = 'disabled'
        print(f'normal')
        sys.stderr.flush()
        sys.stdout.flush()
 
    except Exception as e:
        print(e)
        process_for_push_stream.kill()
        button_start['state'] = 'normal'
        button_show['state'] = 'disabled'
        button_close['state'] = 'disabled'
        messagebox.showerror('错误','关闭失败')
        sys.stderr.flush()
        sys.stdout.flush()
        pass

    return 0 
def imshow():
    global video
    global root
    global image
    res,img=video.read()
    if flag ==1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)
        image.image=img
        image['image']=img
        root.after(10,imshow)
    else:
        print('发送端已关闭')
        image.config(text='发送端已关闭')
        return 0
def show_video():
    global video
    # video=cv2.VideoCapture(rtsp_server_url)
    
    #rtscapture
    video = RTSCapture.create(rtsp_server_url)
    video.start_read()
    print(video.isOpened())
    if video.isOpened():
        imshow()
        
        # button state
        button_start['state'] = 'disabled'
        button_show['state'] = 'disabled'
        button_close['state'] = 'normal'
    else:
        messagebox.showerror('错误','请先打开发送端，或者检查网络连接')

# Settings Variable
root = tkinter.Tk()
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.resizable(False, False)
root.title('发送端')

    # 注册 label widget 帧率 比特率 压缩比
frame_label = tkinter.Label(root, text='总帧数', font= (1))
frame_rate_label = tkinter.Label(root, text='帧率:',font= (1))
qp_label = tkinter.Label(root, text='量化参数:',font= (1))
size_label = tkinter.Label(root, text='码流大小:',font= (1))
time_label = tkinter.Label(root, text='时间:',font= (1))
bit_rate_label = tkinter.Label(root, text='比特率:', font= (1))
speed_label = tkinter.Label(root, text='编码速度:', font= (1))

    # 标签位置
frame_label.grid(row=0, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)
frame_rate_label.grid(row=1, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)
qp_label.grid(row=2, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)
size_label.grid(row=3, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)
time_label.grid(row=4, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)
bit_rate_label.grid(row=5, column=0,columnspan=1, sticky=tkinter.N+tkinter.W, padx=5,pady=5)
speed_label.grid(row=6, column=0,columnspan=1, sticky=tkinter.N+tkinter.W,padx=5,pady=5)


    # 标签内容
    # 在 output_video_msg 方法中更新


    # 注册 button widget 打开 关闭
button_start = tkinter.Button(root, text='打开', command=start_push_stream , font=(30),width=10,height=2)
button_show = tkinter.Button(root, text='显示画面', command=show_video , font=(30),width=10,height=2,state='disabled')
button_close = tkinter.Button(root, text='关闭', command=close_push_stream , font=(30),width=10,height=2,state='disabled')

    # 按钮位置
button_start.grid(row=7, column=0,columnspan=1, padx=5,pady=5,sticky=tkinter.N+tkinter.W)
button_show.grid(row=8, column=0,columnspan=1, padx=5,pady=5,sticky=tkinter.N+tkinter.W)
button_close.grid(row=9, column=0, columnspan=1,padx=5,pady=5,sticky=tkinter.N+tkinter.W )

#     #创建label显示视频
image = tkinter.Label(root, text='仍未推流', 
                    #   width=VIDEO_WIDTH, 
                    #   height=VIDEO_HEIGHT
                    )
image.grid(row=0, column=1,rowspan=10,columnspan=1, sticky=tkinter.N+tkinter.E)


if __name__ == '__main__':

    root.mainloop()
    # video.release()
    os.system('taskkill /f /im %s' % 'ffmpeg.exe')
    # kill second utils_server.exe
    os.system('taskkill /f /im %s' % 'utils_server.exe')
    os.system('taskkill /f /im %s' % 'mediamtx.exe')
    # os._exit()
    root.quit()

