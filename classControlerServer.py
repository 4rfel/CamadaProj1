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

# stdscr = curses.initscr()
# curses.noecho()
# curses.cbreak()

class ControlerServer():
    def __init__(self):
        self.extension = None
        self.messageRead = None

        self.com = enlace(serialName)
        self.com.enable()
        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self._resp_ = {0x01:"EoP not found",0x02:"EoP wrong position",0x03:"payLoadSize != realPayloadSize",0x04:"Wrong package number",0x05:"Success",0x06:"Timeout",0xff:None}
        self.extension_types_reverse = {0x00:"txt",0x01:"py",0x02:'png',0x03:'jpg',0x04:'jpeg',0x05:'pdf',0x06:'gif',0x07:'docx',0x08:'js',0x09:'java',0x0a:'dll'}
        
        self.response = None
        self.timeout = False
        self.time = time()
        self.throughput = 0
        self.overhead = 0

        self.fullFile = None
        self.readPackage()

    def sendPackage(self):
        self.time = time()
        self.com.sendData(self.response)
        if self.timeout:
            self.sendPackage()
            sleep(0.1)
        self.readPackage()


    def readPackage(self):
        while self.com.rx.getIsEmpty():
            pass
        head, headSize = self.com.getData(12)
        headDismounter = HeadDismounter(head)
        self.extension = self.extension_types_reverse[headDismounter.getExtension()]
        self.packageNumberSent = headDismounter.getPackageNumber()
        payLoadSize = headDismounter.getPayLoadSize()
        print(f"payLoad size: {payLoadSize}")
        package, packageSize = self.com.getData(payLoadSize+4)
        self.throughput = 1/(time() - self.time)
        self.overhead = (packageSize + headSize)/payLoadSize
        packageRead = PackageDismounter(package, head)
        payLoad = packageRead.getPayLoad()
        packageNumber = packageRead.getPackageNumber()
        totalOfPackages = packageRead.getTotalOfPackages()
        self.printProgressBar(packageNumber, totalOfPackages,self.throughput,self.overhead)
        self.response = packageRead.getResponse()

        if self.fullFile != None:
            self.fullFile += payLoad
        else:
            self.fullFile = payLoad
        if packageNumber >= totalOfPackages:
            newfilename = input("Nome para o novo arquivo: ")
            self.saveFile(newfilename)
        else:
            self.sendPackage()
        
        
    def saveFile(self, filename):
        if self.fullFile != None:
            with open("fotos/" + filename + "." + self.extension, "wb") as file:
                file.write(self.fullFile)
            self.com.disable()            
        else:
            pass
    
    def printProgressBar (self, packageNumber, totalOfPackages,tp,oh):
        # progressBar(packageNumber, totalOfPackages, tp, oh, "0x05")
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

controlerServer = ControlerServer()

print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")
