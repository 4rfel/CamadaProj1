from classPackage import PackageMounter, PackageDismounter, Head
from math import ceil, floor
from enlace import enlace
import subprocess
from time import sleep, time, localtime
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
        # self.file = bytes([0x02])*23 + bytes([0xd4])*12 + bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4]) + bytes([0xa2])*23 + bytes([0x8b])*12
        self.file_size = len(self.file)
        # print(self.file_size)
        self.current_package = 1
        self.current_package_bytes = self.current_package.to_bytes(3,"big")
        self.leftover = None
        self.timer_ini = time()

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
        self.total_of_packages_bytes = self.total_of_packages.to_bytes(3,"big")

        self.inicia = False

        self.extension = filepath.split(".")[-1].lower()
        self.extension_bytes = bytes([self.extension_types[self.extension]])

    def run(self):
        while not self.inicia:
            # print("Phase 1")
            self.send_0x01_check_0x02()
        while self.current_package <= self.total_of_packages:
            # print(self.current_package*2**7)
            print(f"\rTotal de pacotes / Pacote Atual: {self.total_of_packages} {self.current_package}  Porcentagem: {round(100*self.current_package/self.total_of_packages,4)}%",end="\r")
            self.send_package()
            self.timer_resend = self.timer_timeout = time()
            self.check_0x04()
        
        print(f"Throughput: {self.file_size/(time() - self.timer_ini)}")
        print("Tamanho do pacote: ",self.file_size)
        print("--- Success ---")
        self.close_connection()

    def updateLog(self, msg, client_number, rem_dest, end, received_sent):
        time_var = localtime()
        year = time_var.tm_year
        month = time_var.tm_mon
        day = time_var.tm_mday
        hour = time_var.tm_hour
        minuto = time_var.tm_min
        sec = time_var.tm_sec
        date = f"{year}/{month}/{day} --- {hour}:{minuto}:{sec}"
        text = f"Msg: {msg} --{received_sent}  {date}   {rem_dest}: {client_number}\n"
        with open("client_log.txt", "a") as log:
            log.write(text)
        if end:
            with open("client_log.txt", "a") as log:
                log.write("====================================================================\n\n ")
            
    def send_package(self):
        if self.leftover != None:
            payload = self.leftover + self.file[(self.current_package-1)*2**7:self.current_package*2**7]
        else:
            payload = self.file[(self.current_package-1)*2**7:self.current_package*2**7]
        msg = bytes([0x03])
        head = self.current_package.to_bytes(3,"big") + msg + self.total_of_packages_bytes + self.extension_bytes + bytes([0x01])
        mounter = PackageMounter(head, payload)
        self.leftover = mounter.get_leftovers()
        package = mounter.get_package()
        # print(package)
        self.com.sendData(package)
        self.updateLog(msg, 1, "Servidor", False, "Sent")
        
    def send_0x01_check_0x02(self):
        # print("Sending T1 massage")
        msg = bytes([0x01])
        self.send_msg(0x01)
        self.updateLog(msg, 1, "Servidor", False, "Enviado")
        t0 = time()
        recived_response = True
        while self.com.rx.getIsEmpty():
            t1 = time() - t0
            if t1 > 5:
                print("Timeout +5")
                recived_response = False
                break
        if recived_response:
            # print("getting data response 1")
            head_bytes, _ = self.com.getData(10)
            # self.com.fisica.flush()
            head = Head(head_bytes)
            _, _ = self.com.getData(head.get_payload_size()+4)
            msg = head.get_message()
            if msg == 0x02:
                self.updateLog(msg, 1, "Servidor", False, "Recived")
                self.inicia = True
                    
    def check_0x04(self):
        # print("Checking T4 msg")
        recived_response = True
        # print("Phase 2")
        while self.com.rx.getIsEmpty():
            t1 = time() - self.timer_resend
            # print(f"timer {t1}")
            if t1 > 5:
                print("\nTimer 1 reached 5 seconds\n")
                recived_response = False
                break
            t2 = time() - self.timer_timeout
            if t2 > 20:
                print("\nTimeOut\n")
                self.close_connection()
                break
        if recived_response:
            # print("Recebeu Resposta")
            head_bytes, _ = self.com.getData(10)
            # print(f"head bytes: {head_bytes}")
            head = Head(head_bytes)
            msg_1 = head.get_message()
            _ = self.com.getData(head.get_payload_size()+4)
            # print(f"msg: {msg_1}")
            if msg_1 != 0x04 and msg_1 != 0x06:
                self.updateLog(msg_1, 1, "Recived", True, "Servidor")
                self.close_connection()
            if msg_1 == 0x04:
                print("\nRecieved t4...\n")
                self.current_package = head.current_package + 1
                self.updateLog(msg_1, 1, "Recived", False, "Servidor")
            elif msg_1 == 0x06:
                self.updateLog(msg_1, 1, "Recived", False, "Servidor")
                self.com.fisica.flush()
                # print("----------------------LEFTOVERS--------------------------")
                # print(self.leftover)
                # print("---------------------------------------------------------")
                self.current_package = head.get_current_package()
                print("\nResending...\n")
                # self.close_connection()
        else:
            if self.current_package < self.total_of_packages:
                self.send_package()
                self.updateLog(3, 1, "Sent", False, "Servidor")
                self.timer_resend = time()           

    
    def send_msg(self, msg):
        head = self.current_package_bytes + bytes([msg]) + self.total_of_packages_bytes + self.extension_bytes + bytes([0x01])
        mounter = PackageMounter(head,bytes([0x00]))
        package = mounter.get_package()
        # print("Sending package:"+f"{package}")
        self.com.sendData(package)
        self.updateLog(msg, 1, "Recived", False, "Servidor")

    def close_connection(self):
        print("\n----DISABLING----\n")
        msg = 0x05
        self.send_msg(0x05)
        self.updateLog(msg, 1, "Sent", True, "Servidor")
        self.com.disable()
        exit()


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
#serialName = serial.tools.list_ports.comports()[0][0]
#print(f"Porta: {serialName}")

serialName = "/dev/ttyACM0"

root = Tk()
root.withdraw()

filepath = filedialog.askopenfilename()

controlerClient = ControlerClient(filepath, serialName)
controlerClient.run()

# newfilename = input("Nome para o novo arquivo: ")
# controlerServer.saveFile("Chegada")