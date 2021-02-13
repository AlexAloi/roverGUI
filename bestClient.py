import threading
import socket
import time
from imutils.video import VideoStream
import imagezmq
import numpy as np

class ItemStream:
    def __init__(self, ip):
        self.camDict = dict()
        self.senders = [imagezmq.ImageSender(connect_to='tcp://'+ip+':5555'),imagezmq.ImageSender(connect_to='tcp://'+ip+':8888')]
        #192.168.0.13

    def addImageStream(self, id, src, sender):
        imgStream = ImageStream(src, id, self.senders[sender])
        self.camDict[id] = imgStream

    def removeImageStream(self, id):    
        if id in self.camDict:
            self.camDict[id].stop()
            del self.camDict[id]
        else:
            sendConsole("ERROR: camera ID not found when attemping to remove stream")

    def sendText(self, id, data):
        text = np.array([id,data])
        self.senders[0].send_image("text", text)

    def sendConsole(self, msg):
        self.senders[0].send_image("console", np.array([msg]))

class ImageStream:
    def __init__(self, src, id, sender):
        self.id = id
        self.src = src
        self.sender = sender
        self.thread = threading.Thread(target=self.imageLoop, args=())
        self.thread.start()

    def imageLoop(self):
        picam = VideoStream(src=self.src).start()
        time.sleep(2.0)  # allow camera sensor to warm up
        while True:  # send images as stream until Ctrl-C
           image = picam.read()
           self.sender.send_image(self.id, image)

    def stop(self):
        self.thread.join()

if __name__ == "__main__":
    b = ItemStream("192.168.0.13")
    b.sendConsole("lmao")
    b.sendText("charge",15)
    b.addImageStream("front", 0, 0)
