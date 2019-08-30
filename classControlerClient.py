from classPackage import PackageMounter, PackageDismounter, Head
from math import ceil, floor
from enlace import enlace
import subprocess
from time import sleep, time
from tkinter import filedialog, Tk
from sys import exit


def install(name):
    subprocess.call(['pip', 'install', name])

def progressBar(currentPackage, totalPacotes, Throughput, Overhead, message):
    a = floor((currentPackage/totalPacotes)*100)
    stdscr.addstr(0,   0,  "currentPackage"                                 )
    stdscr.addstr(0, 115,  "Total of Packages"                             )
    stdscr.addstr(1,   0, f"{currentPackage}"                               )
    stdscr.addstr(1, 125, f"{totalPacotes}"                                )
    stdscr.addstr(1,  13,  "[" + "#"*a + "-"*(100-a) + "]"                 )    
    stdscr.addstr(3,   0, f"Throughput: {Throughput} packages/second"      )
    stdscr.addstr(4,   0, f"Overhead  : {Overhead} PackageSize/PayLoadSize")
    stdscr.addstr(5,   0, f"Message   : {message}")

    stdscr.refresh()

    if currentPackage==totalPacotes-1:
        print(f"""currentPackage                                                                                                      Total of Packages
{currentPackage+1}          [####################################################################################################]          {totalPacotes}

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

class ControlerClient():
    def __init__(self, filepath, serial_name):
        with open(str(filepath),"rb") as logo:
            self.file = logo.read()
        self.file_size = len(self.file)
        self.current_package = 1
        self.leftover = None

        self.com = enlace(serial_name)
        self.com.enable()

        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,
        'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}

        self.extension_types_reverse = {0x00:"txt",0x01:"py",'png':0x02,'jpg':0x03,'jpeg':0x04,
        'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}

        self._resp_ = {0x01:"connection request",0x02:"connection granted",0x03:"sending data"
		,0x04:"success",0x05:"timeout",0x06:"error"}

        self.message_read = bytes()
        self.time = time()
        #self.package_number_sent = 1
        self.total_of_packages = ceil(self.file_size/128)

        self.inicia = False

        self.extension = filepath.split(".")[-1].lower()
        self.extensionByte = bytes([self.extension_types[self.extension]])

    def run(self):
        if not self.inicia:
            msg = bytes([0x01])
            #      packageNumber*3 + msg*1 + totalPackages*3 + extension*1   + servidor number*1 + payload size*1 = 10bytes
            head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])     + bytes([0x01]) 
            montador = PackageMounter(head, bytes([0x00]))
            contato = montador.get_package()
            self.com.sendData(contato)
            sleep(5)
            if self.com.rx.getIsEmpty():
                print("Trying new connection")
                self.run()
            response_server = self.com.getData(10)
            head = Head(response_server)
            if head.get_server_number != 0x01:
                self.run()
            else:
                self.inicia = True
                self.package_number_sent = 1
                self.send_package()

    def send_package(self):
        if self.package_number_sent <= self.total_of_packages:
            if self.leftover!=None:
                payload = self.leftover + self.file[(self.package_number_sent-1)*2**7:self.package_number_sent*2**7]
            else:
                payload = self.file[(self.package_number_sent-1)*2**7:self.package_number_sent*2**7]

            msg = bytes([0x03])
            #      packageNumber*3 + msg*1 + totalPackages*3 + extension*1   + servidor number*1 + payload size*1 = 10bytes
            head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])     + bytes([0x01])
            montador = PackageMounter(head, payload)
            package = montador.get_package()
            self.com.sendData(package)
            self.timer_resent = time()
            self.timer_timeout = time()
            self.read_package()
        else:
            print("Finalizado")
            exit()
        

    def read_package(self):
        head_bytes = self.com.getDataTimer(10,self.timer_timeout)
        head = Head(head_bytes)
        if head.get_server_number == bytes([0x01]) or head.get_message == bytes([0x04]):
            payload_eop, payload_eop_size = self.com.getDataTimer(head.get_payload_size+4)
            dismounter = PackageDismounter(payload_eop, head)
            self.package_number_sent += 1
            self.send_package()
        else:
            if self.timer_resent-time() > 5:
                msg = bytes([0x03])
                head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])  + bytes([0x01])
                montador = PackageMounter(head, bytes([0x00]))
                package = montador.get_package()
                self.com.sendData(package)
                self.timer_resent = time()

            if self.timer_timeout-time() > 20:
                msg = bytes([0x05])
                head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])  + bytes([0x01])
                montador = PackageMounter(head, bytes([0x00]))
                package = montador.get_package()
                self.com.sendData(package)
                self.com.disable()
                exit()

            else:
                head_bytes, head_size = self.com.getDataTimer(10,self.timer_timeout)
                if head_size == -1:    
                    head = Head(head_bytes)                    
                elif head.get_message == 0x06:
                    head = Head(head_bytes)
                    payload_size = head.get_payload_size()
                    payload_eop , payload_eop_size = self.com.getDataTimer(payload_size+4, self.timer_timeout)
                    if payload_eop_size != -1:
                        self.package_number_sent = head.get_package_number
                    msg = bytes([0x03])
                    head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])  + bytes([0x01])
                    montador = PackageMounter(head, bytes([0x00]))
                    package = montador.get_package()
                    self.com.sendData(package)
                    self.timer_resent = time()
                    self.timer_timeout = time()
                self.read_package()

'''
response:
	- 0x01: connection request
	- 0x02: connection granted 
	- 0x03: sending data
	- 0x04: success
	- 0x05: timeout
	- 0x06: error

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

# print(serial.tools.list_ports.comports()[0])
serialName = serial.tools.list_ports.comports()[0][0]

root = Tk()
root.withdraw()

filepath = filedialog.askopenfilename()

controlerClient = ControlerClient(filepath, serialName)
controlerClient.run()
com.disable()

# newfilename = input("Nome para o novo arquivo: ")
# controlerServer.saveFile("Chegada")