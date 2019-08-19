from classPackage import PackageMounter, PackageDismounter, HeadDismounter
from math import ceil, floor
from enlace import enlace
import subprocess
from time import sleep, time

from tkinter import filedialog, Tk


def install(name):
    subprocess.call(['pip', 'install', name])

def progressBar(ActualPackage, totalPacotes, Throughput, Overhead, message):
    a = floor((ActualPackage/totalPacotes)*100)
    stdscr.addstr(0,   0,  "ActualPackage"                                 )
    stdscr.addstr(0, 115,  "Total of Packages"                             )
    stdscr.addstr(1,   0, f"{ActualPackage}"                               )
    stdscr.addstr(1, 125, f"{totalPacotes}"                                )
    stdscr.addstr(1,  13,  "[" + "#"*a + "-"*(100-a) + "]"                 )    
    stdscr.addstr(3,   0, f"Throughput: {Throughput} packages/second"      )
    stdscr.addstr(4,   0, f"Overhead  : {Overhead} PackageSize/PayLoadSize")
    stdscr.addstr(5,   0, f"Message   : {message}")

    stdscr.refresh()

    if ActualPackage==totalPacotes-1:
        print(f"""ActualPackage                                                                                                      Total of Packages
{ActualPackage+1}          [####################################################################################################]          {totalPacotes}

Throughput: {Throughput} packages/second
Overhead  : {Overhead} PackageSize/PayLoadSize
Message: {message}""")
    
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
        self.totalOfPackages = ceil(self.fileSize/2**16)
        self.actualPackage = 1
        self.leftover = None
        self.EOP = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])

        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self._resp_ = {0x01:"EoP not found",0x02:"EoP wrong position",0x03:"payLoadSize != realPayloadSize",0x04:"Wrong package number",0x05:"Success",0x06:"Timeout",0xff:None}
        self.extension_types_reverse = {0x00:"txt",0x01:"py",'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self.messageRead = None
        self.time = time()
        self.packageNumberSent = 1

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
        
        print(len(payload))
        if self.packageNumberSent <= self.totalOfPackages:
    #              packageNumber                           response        totalPackages                             extension         
            head = self.actualPackage.to_bytes(4, "big") + bytes([0xff]) + self.totalOfPackages.to_bytes(4, "big") + self.extensionByte
            packageMounter = PackageMounter(head=head, payLoad=payload, EOP=self.EOP)
            package = packageMounter.getPackage()
            print("sending package")
            # self.com.sendData(package)
            self.time = time()
            com.sendData(package)
            print("package sent")
            self.readPackage()

    def readPackage(self):
        while com.rx.getIsEmpty():
            pass
        print("client read")

        head, headSize = com.getData(12)

        headDismounter = HeadDismounter(head)
        self.packageNumberSent = headDismounter.getPackageNumber()
        payLoadSize = headDismounter.getPayLoadSize()
        package, packageSize = com.getData(payLoadSize+4)
        dt = 1/(time()-self.time)
        print("Throughput: ",dt, dt**(-1))

        packageRead = PackageDismounter(package, head)

        print(package)

        self.messageRead = packageRead.getMessage()
        self.messageInterpreter()

    def messageInterpreter(self):
        if self.messageRead==0x01:
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

    def printProgressBar (self, packageNumber, totalOfPackages):
        # progressBar(packageNumber, totalOfPackages, 10, 2, "0x05")
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

# controlerServer = ControlerServer()

com.disable()
print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")

# newfilename = input("Nome para o novo arquivo: ")
# controlerServer.saveFile("Chegada")