import threading
import socket
import time
from imutils.video import VideoStream
import imagezmq
import numpy as np

class ItemStream:
    def __init__(self, ip):
        self.camDict = dict()
        self.cameras = 0
        self.cameraList = ["front", "drive"]
        self.senders = [imagezmq.ImageSender(connect_to='tcp://'+ip+':5555')]
        #192.168.0.13

    def addImageStream(self, src):
        imgStream = ImageStream(src, self.cameraList[self.cameras], self.senders[0])
        self.camDict[id] = imgStream
        self.cameras += 1

    def removeImageStream(self, id):    
        if id in self.camDict:
            self.camDict[id].stop()
            del self.camDict[id]
            self.cameras -= 1
        else:
            sendConsole("ERROR: camera ID not found when attemping to remove stream")
            

    def sendText(self, id, data):
        text = np.array([id,data])
        self.senders[0].send_image("text", text)

    def sendConsole(self, msg):
        self.senders[0].send_image("console", np.array([msg]))

    def closeStream(self):
        for cam in self.camDict.items():
            cam[1].stop()
            


class ImageStream:
    def __init__(self, src, id, sender):
        self.id = id
        self.src = src
        self.sender = sender
        self.running = True
        self.thread = threading.Thread(target=self.imageLoop, args=())
        
        self.thread.start()

    def imageLoop(self):
        picam = VideoStream(src=self.src).start()
        time.sleep(2.0)  # allow camera sensor to warm up
        
        while self.running:  # send images as stream until Ctrl-C
           image = picam.read()
           self.sender.send_image(self.id, image)

    def stop(self):
        self.running = False
        self.thread.join()

if __name__ == "__main__":
    b = ItemStream("192.168.0.13")
    b.sendConsole("lmao")
    b.sendText("charge",15)
    b.addImageStream(0)
    msg = ""
    while msg.lower() != "y":
        msg = input("Close the program? (y/n) ")
    b.closeStream()
