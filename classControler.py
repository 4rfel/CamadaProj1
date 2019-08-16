from classPackage import PackageMounter, PackageDismounter, HeadDismounter
from tkinter import filedialog, Tk
from math import ceil
from enlace import enlace
import serial
from time import sleep, time

serialName = "COM3"
com = enlace(serialName)
com.enable()

class ControlerClient():
    def __init__(self, filepath):
        with open(str(filepath),"rb") as logo:
            self.file = logo.read()
        self.fileSize = len(self.file)
        self.totalOfPackages = ceil(self.fileSize/128)
        self.actualPackage = 1
        self.leftover = None
        self.extension = None
        self.EOP = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])

        self.messageRead = None

        # self.com = enlace(serialName)
        # self.com.enable()

        self.sendPackage()

    def sendPackage(self):
        if self.leftover!=None:
            payload = self.leftover + self.file[(self.actualPackage-1)*112:self.actualPackage*112]
        else:
            payload = self.file[(self.actualPackage-1)*112:self.actualPackage*112]
#              packageNumber                           response        totalPackages                             extension       ??
        head = self.actualPackage.to_bytes(4, "big") + bytes([0xff]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00]) 
        packageMounter = PackageMounter(head=head, payLoad=payload, EOP=self.EOP)
        package = packageMounter.getPackage()
        # self.com.sendData(package)
        com.sendData(package)
        # print("payload", payload)
        # print("package sent",package)
        # print(self.actualPackage)

    def readPackage(self):
        # head = self.com.getData(12)
        head, headSize = com.getData(12)

        headDismounter = HeadDismounter(head)
        self.packageNumberSent = headDismounter.getPackageNumber()
        head = headDismounter.getHead()
        payLoadSize = head.getPayLoadSize()
        # package = self.com.getData(payLoadSize)
        package, packageSize = com.getData(payLoadSize+4)

        packageRead = PackageDismounter(package, head)
        self.messageRead = packageRead.getMessage()
        self.messageInterpreter()

    def messageInterpreter(self):
        if   self.messageRead==0x01:
            self.sendPackage()
        elif self.messageRead==0x02:
            self.sendPackage()
        elif self.messageRead==0x03:
            self.sendPackage()
        elif self.messageRead==0x04:
            self.actualPackage = self.packageNumberSent
            self.sendPackage()
        elif self.messageRead==0x05:
            self.actualPackage += 1
            self.sendPackage()
        elif self.messageRead==0x06:
            self.sendPackage()

class ControlerServer():
    def __init__(self):
        self.extension = None
        self.messageRead = None

        # self.com = enlace(serialName)
        # self.com.enable()
        
        self.response = None
        self.timeout = False

        self.fullFile = None

        self.readPackage()

    def sendPackage(self):
        # self.com.sendData(self.response)
        com.sendData(self.response)

        if self.timeout:
            self.sendPackage()
            sleep(0.1)

    def readPackage(self):
        # head = self.com.getData(12)
        head, headSize = com.getData(12)
        # print("head read", head)
        headDismounter = HeadDismounter(head)
        self.packageNumberSent = headDismounter.getPackageNumber()
        payLoadSize = headDismounter.getPayLoadSize()
        # package = self.com.getData(payLoadSize)
        package, packageSize = com.getData(payLoadSize+4)
        packageRead = PackageDismounter(package, head)
        # print("package read", package)
        payLoad = packageRead.getPayLoad()
        # print("payLoad read", payLoad)
        self.response = packageRead.getResponse()
        if self.fullFile != None:
            self.fullFile += payLoad
        else:
            self.fullFile = payLoad
        self.sendPackage()
        
        
    def saveFile(self, filename):
        if self.fullFile != None:
            with open(filename + ".jpeg", "wb") as file:
                file.write(self.fullFile)
        else:
            pass
'''
response:
	- 0x01: EOP not found
	- 0x02: EOP wrong position
	- 0x03: payLoadSize != realPlayLoadSize
	- 0x04: wrong packageNumber
	- 0x05: success 
	- 0x06: timeout
	- 0xff: none

extension:
	- 0x00: .txt
	- 0x01: .py
	- 0x02: .png
	- 0x03: .jpg
	- 0x04: .jpeg
	- 0x05: .pdf
	- 0x06: .gif
	- 0x07: .docx
	- 0x08: .js
	- 0x09: .java
	- 0x0a: .dll
	- 0xff: sem extensão
'''

root = Tk()
root.withdraw()

filepath = filedialog.askopenfilename()

controlerClient = ControlerClient(filepath=filepath)

controlerServer = ControlerServer()
controlerServer.saveFile("test")

print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
com.disable()