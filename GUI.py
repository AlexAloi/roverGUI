from PIL import Image
from PIL import ImageTk
import tkinter as tk
import imutils
import imagezmq
import cv2
import threading
import json
import argparse

class GUI:
    def __init__(self, master):
        self.master = master
        self.cameraSize = (int(aspectr[0]*aspectr[2]/2),int(aspectr[1]*aspectr[2]/2))
        self.deadFrame = cv2.resize(cv2.cvtColor(cv2.imread("lmao.png"),cv2.COLOR_BGR2RGB),self.cameraSize)
        self.deadFrame = Image.fromarray(self.deadFrame)
        self.deadFrame = ImageTk.PhotoImage(self.deadFrame)
        self.thread = None
        self.stopEvent = None
        self.createScreen()

    def createScreen(self):
        self.mainCanvas = tk.Canvas(master=self.master,width=aspectr[0]*aspectr[2],height=aspectr[1]*aspectr[2], bg="BLACK")
        self.mainCanvas.pack()

        elements = self.getElements()
        self.elements = dict()
        if "image" in elements.keys():
            lengthMod = len(elements["image"])
        else:
            lengthMod = 1
        if lengthMod > 1:
            cameraSize = (int(aspectr[0]*aspectr[2]/lengthMod),int(aspectr[1]*aspectr[2]/lengthMod))
        else:
            cameraSize = (int(aspectr[0]*aspectr[2]/2),int(aspectr[1]*aspectr[2]/2))

        self.deadFrame = cv2.resize(cv2.cvtColor(cv2.imread("lmao.png"), cv2.COLOR_BGR2RGB),cameraSize)
        self.deadFrame = Image.fromarray(self.deadFrame)
        self.deadFrame = ImageTk.PhotoImage(self.deadFrame)
        i = 0
        if "image" in elements.keys():
            self.elements["image"] = dict()
            for graphic in elements["image"]:

                self.elements["image"][graphic] = Graphic(self.mainCanvas, (i%lengthMod*cameraSize[0],int(i/lengthMod)*cameraSize[1]), cameraSize, self.deadFrame)
                i += 1

        i = 0
        self.elements["text"] = dict()
        for text in elements["text"]:
            strtext = elements["text"][text]
            self.elements["text"][text] = Text(self.mainCanvas, (10+cameraSize[0]*int(i/10), cameraSize[1]+(i+1)*21), strtext[0], strtext[1])
            i += 1

        self.elements["other"] = dict()
        for other in elements["other"]:
            print(other)
            if other == "CONSOLE_LOG":

                self.elements["other"][other] = Console(self.mainCanvas,(cameraSize[0], aspectr[1]*aspectr[2] - cameraSize[1]), cameraSize)

        
        self.image_hub = imagezmq.ImageHub()
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
            
    def getElements(self):
        global packages
        elements = dict()

        for p in packages:
            with open("GUIpackages/"+p+".json") as f:
                data = json.load(f)
            elements = merge(elements, data)

        return elements

    def videoLoop(self):
        print("HERE")
        while True:
            name, data = self.image_hub.recv_image()
            if name == "text":
                self.elements["text"][data[0]].updateData(data[1])
            elif name == "console":
                self.elements["other"]["CONSOLE_LOG"].addLog(data[0])
            else:
                self.elements["image"][name].updateImage(data)
            
            self.image_hub.send_reply(b"OK")


class Graphic:
    def __init__(self, canvas, canvasXY, size, frame):
        self.canvas = canvas
        self.canvasXY = canvasXY
        self.size = size
        self.frame = frame
        self.canvasImage = self.canvas.create_image(canvasXY[0], canvasXY[1], image=self.frame, anchor="nw")

    def updateImage(self, image):
        print("updating image")
        frame = cv2.resize(cv2.cvtColor(image,cv2.COLOR_BGR2RGB),self.size)
        frame = Image.fromarray(frame)
        self.frame = ImageTk.PhotoImage(frame)
        self.canvas.itemconfigure(self.canvasImage,image=self.frame )

class Text:
    def __init__(self, canvas, canvasXY, pretext, postext):
        self.canvas = canvas
        self.canvasXY = canvasXY
        self.pretext = pretext
        self.postext = postext
        self.dataText = None
        self.canvasImage = self.canvas.create_text(canvasXY[0], canvasXY[1], text=self.pretext+str(self.dataText)+self.postext, anchor="nw", fill="white")

    def updateData(self, text):
        self.dataText = text
        self.canvas.itemconfigure(self.canvasImage,text=self.pretext+str(text)+self.postext)

class Console:
    def __init__(self, canvas, canvasXY, wh):
        self.canvas = canvas
        self.canvasXY = canvasXY
        x,y = self.canvasXY[0], self.canvasXY[1]
        w,h = wh[0] - 20, wh[1] - 40
        print(x, y, w, h)
        self.canvas.create_rectangle(x,y,x+w,y+h, outline="red")
        self.canvas.create_text(x+w/2,y+10, text="CONSOLE", fill="white")
        self.log = self.canvas.create_text(x,y+20, text="LOG 1", fill="white", anchor="nw", width=w)
        self.texts = ["Logs"]
        self.addLog("Starting GUI")

    def addLog(self, text):
        self.texts.append(text)
        if len(self.texts) > 16:
            self.texts = self.texts[1:]
        self.canvas.itemconfigure(self.log, text="\n".join(self.texts))
        with open("GUIlog.txt","a") as f:
            f.write("\n"+text)

def merge(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

if __name__ == "__main__":
    aspectr=[16,9,75]
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--packages", help = "PACKAGES TO ADD")
    args = vars(ap.parse_args())
    if args["packages"] == None:
        packages = ["default"]
    else:
        packages = str(args["packages"]).split(",")
        packages.append("default")

    root = tk.Tk()
    app = GUI(root)
    root.title("JETSON GUI")
    root.mainloop()
    
    
