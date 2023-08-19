import socket

# for ffmpeg

# rtsp settings
rtsp_server_ip = socket.gethostbyname(socket.gethostname())
rtsp_server_port = "8554"
rtsp_server_url = f"rtsp://{rtsp_server_ip}:{rtsp_server_port}/mystream"

rtp_server_url = f"rtp://{rtsp_server_ip}:8000/mystream"
# rtsp_server_url = rtsp://192.168.31.17:8554/mystream
print(rtsp_server_url)
# ffmpeg Push stream settings
stream_params = {
    "-f" : "rtsp",
    "-rtsp_transport": "tcp",
    "-vcodec": "libx265", # define custom Video encoder h.265 
    "GOP": "15", # 参考帧

    "-preset": "fast", # for low latency
    "-tune" : "zerolatency", # for low latency
    'pipe':'', # 用于在推送端获取比特率
}

stream_params2 = {
    "-f" : "rtp",
    "-vcodec": "libx265", # define custom Video encoder h.265
    "-sdp_file": "rtp.sdp",
}

