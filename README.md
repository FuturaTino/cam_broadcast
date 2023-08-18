

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



![image-20230818112007241](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818112007241.png)

![image-20230818112038978](https://github.com/FuturaTino/TyporaImages/raw/main//TyporaImages/image-20230818112038978.png)

## 分解步骤



实现发送端采集编码推流,接收端拉流播放的目标,我把任务分解为以下步骤:

**发送端:**

1. 导入cv2、vidgear、ffmpeg-python库
2. 使用cv2打开摄像头捕获视频帧
3. 对采集到的帧进行h265编码（可以用OpenCV或者FFmpeg进行编码）
4. 创建vidgear的StreamGear对象,指定推流参数中协议为为RTSP（steamGear或 WriteGear）
5. 在循环中不断读取编码后的视频帧,并用StreamGear推送RTSP流
6. 推流地址为RTSP服务器,比如 mediaMXT、SRS（最好）、Wowza或Nginx
7. 添加组件

**接收端:**

1. 导入vidgear cv2 ffmpeg-python 等库
2. 创建vidgear的StreamGear对象,指定拉流参数为RTSP
3. 调用StreamGear去指定的RTSP服务器地址拉取流
4. 在循环中读取StreamGear的帧数据
5. 将解码后的帧显示到OpenCV窗口或Tkinter界面上
6. 添加控制按钮等界面组件



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


