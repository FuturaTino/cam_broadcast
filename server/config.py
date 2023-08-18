# for ffmpeg

# rtsp settings
rtsp_server_ip = "192.168.31.17"
rtsp_server_port = "8554"
rtsp_server_url = f"rtsp://{rtsp_server_ip}:{rtsp_server_port}/mystream"

rtp_server_url = f"rtp://{rtsp_server_ip}:8000/mystream"
# rtsp_server_url = rtsp://192.168.31.17:8554/mystream

# ffmpeg Push stream settings
stream_params = {
    "-f" : "rtsp",
    "-rtsp_transport": "tcp",
    "-vcodec": "libx265", # define custom Video encoder h.265 
    # "-bufsize": "2000k", 
    # "-threads": "2",
    # "-tune" : "zerolatency" # for low latency
}

stream_params2 = {
    "-f" : "rtp",
    "-vcodec": "libx265", # define custom Video encoder h.265
    "-sdp_file": "rtp.sdp",
}

