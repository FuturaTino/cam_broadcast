# import required libraries
from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import cv2
from pathlib import Path 
import subprocess
import os 
import sys
import ffmpeg
import socket
from threading import Thread

ip_address = socket.gethostbyname(socket.gethostname())
port= 8554
rtsp_server_url = f"rtsp://{ip_address}:{port}/mystream"

# Instance
# ffmpeg Push stream settings
multi_stream_params = {
    "-f" : "rtsp",
    "-rtsp_transport": "tcp",
    "-vcodec": "libx265", # define custom Video encoder h.265 
    # "-bufsize": "2000k", 
    "-threads": "2",
    "-tune" : "zerolatency" # for low latency
}



# Function
def push_stream():
    stream = CamGear(source=0).start()
    writer = WriteGear(output= rtsp_server_url,
                    compression_mode=True,
                    logging=True,
                #    custom_ffmpeg=rf'D:\Program FIles\ffmpeg-6.0-essentials_build\bin\ffmpeg.exe',
                    **multi_stream_params)  
    """
    yeid frame from stream and write to writer
    """
    # loop over
    while True:
        # read frames from stream
        frame = stream.read()
        cv2.resize(frame, (640, 480))
        # check for frame if Nonetype
        if frame is None:
            break
        # {do something with the frame here}
        # frame = cv2.putText(frame, "WriteGear is Cool!", (10, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # write frame to writer
        writer.write(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
    # Close 
    cv2.destroyAllWindows()
    stream.stop()
    writer.close()


if __name__ == '__main__':
    push_stream()

