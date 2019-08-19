from classPackage import PackageMounter, PackageDismounter, HeadDismounter
from math import ceil
from enlace import enlace
import subprocess
from time import sleep, time
from progressBar import progressBar

from tkinter import filedialog, Tk


def install(name):
    subprocess.call(['pip', 'install', name])

    
try:
    import curses
except ImportError:
    install("windows-curses")
finally:
    import curses
 
try:
    import esptool
except ImportError:
    install("esptool")
finally:
    import esptool

try:
    import serial
except ImportError:
    install("pyserial")
finally:
    import serial


serialName = serial.tools.list_ports.comports()[0][0]

com = enlace(serialName)
com.enable()

# stdscr = curses.initscr()
# curses.noecho()
# curses.cbreak()

class ControlerClient():
    def __init__(self, filepath):
        with open(str(filepath),"rb") as logo:
            self.file = logo.read()
        self.fileSize = len(self.file)
        self.totalOfPackages = ceil(self.fileSize/128)
        self.actualPackage = 1
        self.leftover = None
        self.EOP = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])

        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self._resp_ = {0x01:"EoP not found",0x02:"EoP wrong position",0x03:"payLoadSize != realPayloadSize",0x04:"Wrong package number",0x05:"Success",0x06:"Timeout",0xff:None}
        self.extension_types_reverse = {0x00:"txt",0x01:"py",'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self.messageRead = None

        self.extension = filepath.split(".")[1].lower()
        self.extensionByte = bytes([self.extension_types[self.extension]])

        # self.com = enlace(serialName)
        # self.com.enable()

        self.sendPackage()

    def sendPackage(self):
        if self.leftover!=None:
            payload = self.leftover + self.file[(self.actualPackage-1)*2**16:self.actualPackage*2**16]
        else:
            payload = self.file[(self.actualPackage-1)*2**16:self.actualPackage*2**16]
#              packageNumber                           response        totalPackages                             extension         
        head = self.actualPackage.to_bytes(4, "big") + bytes([0xff]) + self.totalOfPackages.to_bytes(4, "big") + self.extensionByte
        packageMounter = PackageMounter(head=head, payLoad=payload, EOP=self.EOP)
        package = packageMounter.getPackage()
        # self.com.sendData(package)
        com.sendData(package)
        print(len(package))

    def readPackage(self):
        print("client read")

        head, headSize = com.getData(12)

        headDismounter = HeadDismounter(head)
        self.packageNumberSent = headDismounter.getPackageNumber()
        payLoadSize = head.getPayLoadSize()
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

    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total: 
            print()

class ControlerServer():
    def __init__(self):
        self.extension = None
        self.messageRead = None

        # self.com = enlace(serialName)
        # self.com.enable()
        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self._resp_ = {0x01:"EoP not found",0x02:"EoP wrong position",0x03:"payLoadSize != realPayloadSize",0x04:"Wrong package number",0x05:"Success",0x06:"Timeout",0xff:None}
        self.extension_types_reverse = {0x00:"txt",0x01:"py",0x02:'png',0x03:'jpg',0x04:'jpeg',0x05:'pdf',0x06:'gif',0x07:'docx',0x08:'js',0x09:'java',0x0a:'dll'}
        
        self.response = None
        self.timeout = False

        self.fullFile = None

        self.readPackage()

    def sendPackage(self):
        # self.com.sendData(self.response)
        print("Server sent response")
        print(f"Server response {self.response}\n")
        print("")
        com.sendData(self.response)
        if self.timeout:
            self.sendPackage()
            sleep(0.1)

    def readPackage(self):
        head, headSize = com.getData(12)
        headDismounter = HeadDismounter(head)
        self.extension = self.extension_types_reverse[headDismounter.getExtension()]
        self.packageNumberSent = headDismounter.getPackageNumber()
        payLoadSize = headDismounter.getPayLoadSize()
        package, packageSize = com.getData(payLoadSize+4)
        packageRead = PackageDismounter(package, head)
        payLoad = packageRead.getPayLoad()
        packageNumber = packageRead.getPackageNumber()
        totalOfPackages = packageRead.getTotalOfPackages()
        self.printProgressBar(packageNumber, totalOfPackages)
        self.response = packageRead.getResponse()
        if self.fullFile != None:
            self.fullFile += payLoad
        else:
            self.fullFile = payLoad
        self.sendPackage()
        
        
    def saveFile(self, filename):
        if self.fullFile != None:
            print(len(self.fullFile))
            with open(filename + "." + self.extension, "wb") as file:
                file.write(self.fullFile)
        else:
            pass
    
    def printProgressBar (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
        if iteration == total: 
            print()

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

com.disable()
print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")

newfilename = input("Nome para o novo arquivo: ")
controlerServer.saveFile(newfilename)

