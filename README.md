

todo:

- [x] 配置环境 conda 库
- [x] 制作发送端和RTSP服务器，先用mediamtx作为暂时的RTSP服务器。
- [x] 分解第二目标。
- [x] 发送端 - cv2摄像头采集画面
- [x] 发送端 - 对视频进行编码
- [x] 发送端 - tkinter布局，计算各个变量，绑定按钮事件
- [x] 发送端 - vidgear用RTSP协议推流h.265视频流，将推流画面置换摄像头采集画面
- [x] 接收端 - 获取推流画面
- [ ] 接收端- 布置user段，布置两个label，计算变量

# 快速开始

**启动发送端**



1. 测试进程是否能正常运行。先去server/mediamtx目录，点击mediamtx.exe，手动运行，若显示以下内容，则正常。 **保持mediamtx.exe运行** ，进行下一步。

![image-20230818164559231](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818164559231.png)



2. 去server目录，运行utils_server.exe， 若提示安装ffmpeg，等待其安装完成。最终显示以下内容，`Output #0, rtsp, to 'rtsp://<本机ipv4地址>:8554/mystream'`， 则正常。

![image-20230818165016331](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818165016331.png)

关闭mediamtx.exe 和 utils_server.exe进行下一步。



3. 在项目根目录，即requirements.txt所在目录，用pip安装所需要的python包。

```shell
pip install -r requrements.txt 
```

4. 进入server目录，启动推送端，然后开始、显示视频、断开。

```shell
#目录切换到server文件夹，启动推送端GUI
cd  server
python sk_gui.py
```

5. 查询本机的ip地址，打开cmd，查询本机的内网ipv4地址，tcp转rtp包的端口已固定为`8554`。推送端已经自动获取了本机IP地址，直接运行即可。但也要掌握如何手动查看本机IP地址。

```shell
查询ip地址命令
ipconfig
```

推流地址为 `rtsp://192.168.37.16:8554/mystream` 将该ip换为你的ip即可。

6. 进入user目录，启动客户端。**在窗口中手动设置推送端的IP地址**，然后连接、播放、 关闭。一定要设定正确。代码暂时没有写推流url出错的处理函数，输错ip要堵塞20s。

```python
python user.py	
```



# 任务目标

| 组件   | 目标                                                         | UI布局                                                       |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 发送端 | cv2采集电脑摄像头实时数据，将视频帧数据编码为h.265格式。使用RTSP协议将视频流通过TCP推流。 | 布局分为三大块，左上是推流画面，右上是三个标签： 压缩率，帧率，比特率。下方是两个按钮，开始推流，关闭推流。当推流结束，推流画面变黑。 |
| 接收端 | 客户端从流媒体url上拉流，获取画面                            | 布局分为两大块，左边是推流画面，右边是两个标签：时间延迟和吞吐量。当推流结束，推流画面变黑。 |



## 大致思路

1. cv2发送端采集摄像头视频画面
2. ffmpeg对视频进行编码处理
3. 推流到mediaMTX打包
4. 接受端拉流

​	5.**RTSP是应用层**的控制协议,用于控制媒体流的播放、暂停等。RTP与TCP都是传输层协议,RTP负责传输音视频数据。TCP提供可靠的字节流服务。

6. RTSP 和 RTP 常常一起使用,实现流媒体的控制和传输。RTSP 用来控制播放,比如播放、暂停、快进等;RTP 用来打包并传输音视频数据。两者协同工作,RTSP 指示 RTP 发送哪些数据,实现流媒体的控制和传输。
7. 即使在单独使用 RTSP 的情况下,传输的媒体流数据包实际上还是采用 RTP 封装的。RTSP 只是一个控制信令协议,它不具备实际传输媒体流数据的能力。当 RTSP 单独使用时,它所控制的媒体流数据包都是按 RTP 协议进行封装的。
8. 它们都可以运行在 TCP 等传输层协议之上,由传输层协议提供数据包的发送和交付服务。

![image-20230818112007241](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818112007241.png)

![image-20230818112038978](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818112038978.png)

## 分解步骤



实现发送端采集编码推流,接收端拉流播放的目标,我把任务分解为以下步骤:

**发送端:**

1. 导入相关库。
2. 使用cv2打开摄像头捕获视频帧。
3. 对采集到的帧进行h265编码（可以用OpenCV或者FFmpeg进行编码），然后用ffmpeg以rtsp协议封包，以tcp协议传输推送出去。
4. 推流端监控推流画面与参数。通过stdout管道将ffmpeg编码与rtp封装的性能参数写在窗口中；用自定义rtsCapture实例获取rtp包，在推流端观看视频画面。
7. 添加Label，Button组件。

**接收端:**

1. 导入相关库。
2. 输入推流端的rtsp地址，建立连接。创建自定义的rtsCapture实例，多线程的接收rtp包，减少延迟。
3. rtsCapture类封装了cv2.videoCapture与ffmpeg，具有解析rtp包，解码视频流的功能。
6. 添加控制按钮等界面组件。



# 用到的库

在这个流媒体处理和传输的场景中,主要用到了以下Python库和插件:

1. OpenCV

- 用于摄像头视频捕获和帧处理
- 提供各种图像处理和编解码算法，cv2也支持h.265编码

2. vidgear

- Python视频处理和流媒体传输库
- 封装了对RTSP、HLS等协议的支持
- 推送流给RTSP服务器，或自己就成为RTSP服务器

3. FFmpeg

- 功能强大的媒体处理工具
- 支持全面的编码和解码算法H.265
- 可以推送流给RTMP服务器

4. Tkinter

- Python的GUI工具包
- 可以用来显示视频流和构建简单界面

5. Pillow

- Python图像处理库
- 可以对OpenCV读取的帧进行处理
- 提供Tkinter的图像支持

6. threading

- Python的线程库
- 可以用来实现多线程采集和推流



# 评价指标

| 指标        | 简单解释                                                     |
| ----------- | ------------------------------------------------------------ |
| 量化参数 QP | Quantizer Parameter，量化参数，反映了空间细节压缩情况。值越小，量化越精细，图像质量越高，产生的码流也越长。如QP小，大部分的细节都会被保留；QP增大，一些细节丢失，码率降低，但图像失真加强和质量下降。为了兼顾传输效率与视频质量，QP一般为20-2 [QP参数解析](https://blog.csdn.net/liangjiubujiu/article/details/80569391) |
|             |                                                              |



