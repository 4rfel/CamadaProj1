from classPackage import PackageMounter, PackageDismounter, Head
from math import ceil, floor
from enlace import enlace
import subprocess
from time import sleep, time
from curses.textpad import Textbox, rectangle

from tkinter import filedialog, Tk


def install(name):
	subprocess.call(['pip', 'install', name])

def progressBar(current_package, totalPacotes, Throughput, Overhead, message):
	a = (current_package/totalPacotes)*100
	aa = floor(a)
	stdscr.addstr(0,   0,  "Current Package"                                     )
	stdscr.addstr(0, 115,  "Total of Packages"                                 )
	stdscr.addstr(1,   0, f"{current_package}"                                   )
	stdscr.addstr(1, 125, f"{totalPacotes}"                                    )
	stdscr.addstr(1,  13,  "[" + "#"*a + "-"*(100-aa) + "]"                    )    
	stdscr.addstr(3,   0, f"Throughput: {round(Throughput, 4)} packages/second")
	stdscr.addstr(4,   0, f"Overhead  : {Overhead} PackageSize/PayLoadSize"    )
	stdscr.addstr(5,   0, f"Message   : {message}")

	stdscr.clear()

	if current_package==totalPacotes-1:
		print(f"""ActualPackage                                                                                                      Total of Packages
{current_package+1}          [####################################################################################################]          {totalPacotes}

Throughput: {Throughput} packages/second
Overhead  : {Overhead} PackageSize/PayLoadSize
Message   : {message}""")
	
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

def write_curses(string):
	stdscr.addstr(0, 0, string)
	stdscr.clear()


# stdscr = curses.initscr()
# curses.noecho()
# curses.cbreak()
# curses.curs_set(True)
'''
	- 0x01: connection request
	- 0x02: connection granted 
	- 0x03: sending data
	- 0x04: success
	- 0x05: timeout
	- 0x06: error
'''
class ControlerServer():
	def __init__(self, serialName, server_number):
		self.extension     = None
		self.messageRead   = None
		self.server_number = server_number

		self.com = enlace(serialName)
		self.com.enable()
		self.extension_types = {'txt':0x00, 'py':0x01, 'png':0x02, 'jpg':0x03, 'jpeg':0x04
		, 'pdf':0x05, 'gif':0x06, 'docx':0x07, 'js':0x08, 'java':0x09, 'dll':0x0a}

		self.extension_types_reverse = {0x00:"txt", 0x01:"py", 0x02:'png', 0x03:'jpg'
		, 0x04:'jpeg', 0x05:'pdf', 0x06:'gif', 0x07:'docx', 0x08:'js', 0x09:'java', 0x0a:'dll'}

		self._resp_ = {0x01:"connection request", 0x02:"connection granted", 0x03:"sending data"
		, 0x04:"success", 0x05:"timeout", 0x06:"error"}

		self.response   = None
		self.throughput = 0
		self.overhead   = 0
		self.ocioso     = True
		self.fullFile   = bytearray()

		self.run()

	def run(self):
		while self.ocioso:
			# print("estou ocioso")
			self.check_ocioso()
		# print("nao estou ocioso")
		self.check_ocioso()
		while self.current_package < self.total_of_packages:
			# print("")
			# print(f"\rpacote atual: {self.current_package}     total de pacotes: {self.total_of_packages}", end="\r")
			print(f"pacote atual: {self.current_package}     total de pacotes: {self.total_of_packages}")

			# print("\rreading packages", end="\r")
			self.throughput_timer = time()
			self.timer_timeout_start = time()
			self.read_package()
			# self.print_progress_bar(self.current_package, self.total_of_packages, self.throughput, self.overhead, self.msg_sent)
		# filename = self.get_filename()
		filename = input("Filename: ")
		self.saveFile(filename)
		self.close_connection()
	
	def get_filename(self):
		editwin = curses.newwin(1, 30, 10, 1)
		rectangle(stdscr, 9, 0, 11, 42)
		stdscr.refresh()

		box = Textbox(editwin)

		# Let the user edit until Ctrl-G is struck.
		box.edit()
		return box.gather()

	def check_ocioso(self):
		if self.ocioso:
			while self.com.rx.getIsEmpty():
				# write_curses("searching for connection")
				print("searching for connection")
				# print("\rsearching for connection", end="\r")
				sleep(1)
			print("message received")
			# write_curses("message received")
			self.check_msg_0x01()
		else:
			self.send_response(bytes([0x02]))
			self.current_package = 1
			self.timer_timeout_start = time()
			# self.read_package()

	def check_msg_0x01(self):
		# write_curses("checking if message received is type 0x01")
		print("checking if message received is type 0x01")
		head_bytes = self.com.getData(10)[0]
		# print(f"head bytes: {head_bytes}")
		head = Head(head_bytes)
		print(f"head receive: {head_bytes}")
		msg = head.get_message()
		server_number = head.get_server_number()
		self.total_of_packages = head.get_total_of_packages()
		self.message_interpreter(msg, server_number)
		self.extension = head.get_extension()
		print(f"extension: {self.extension}")
		resto_size = head.get_payload_size()
		_ = self.com.getData(resto_size+4)
		# self.com.fisica.flush()
		# print(f"server wanted: {server_number}")
	
	def message_interpreter(self, msg, server_number):
		print("interpreting messages")
		# print(f"message recived: {msg} \nserver number: {server_number}")
		if msg == 0x01:
			if server_number == self.server_number:
				self.ocioso = False

	def send_response(self, msg):
		print("sending response")
#              packageNumber*3 + msg*1 + totalPackages*3 + extension*1   + servidor number*1 + payload size*1 = 10bytes
		head = bytes([0x00])*3 + msg   + bytes([0x00])*3 + bytes([0x00]) + bytes([0x01])
		response_mounter = PackageMounter(head, bytes([0x00]))
		response = response_mounter.get_package()
		self.com.sendData(response)

	def check_timers(self):
		print("checking timers")
		timer1_start = time()
		while self.com.rx.getIsEmpty():
			timer1_elapsed = time() - timer1_start
			timer_timeout_elapsed = time() - self.timer_timeout_start
			if timer_timeout_elapsed > 20:
				print("-----------------")
				print("	   TIMED OUT")
				print("-----------------")
				self.ocioso = True
				self.close_connection()
			elif timer1_elapsed > 2:
				self.send_response(bytes([0x04]))
				self.read_package()

	def read_package(self):
		self.check_timers()
		head_bytes, size = self.com.getDataTimer(10, self.timer_timeout_start)
		if size == -1:
			self.close_connection()
		else:
			head = Head(head_bytes)
			payload_size = head.get_payload_size()
			payload_EOP, size = self.com.getDataTimer(payload_size+4, self.timer_timeout_start)
			if size == -1:
				self.close_connection()
			else:
				package_dismounted = PackageDismounter(payload_EOP, head)
				self.msg_sent = package_dismounted.get_message_sent()
				self.send_response(self.msg_sent)
				if self.msg_sent == bytes([0x04]):
					self.current_package += 1
					payload = package_dismounted.get_payload()
					self.fullFile += payload
					self.overhead   = package_dismounted.get_overhead()
					elapsed_throughput_timer = time() - self.throughput_timer
					self.throughput =  payload_size/elapsed_throughput_timer
		
	def saveFile(self, filename):
		if self.fullFile != None:
			with open("fotos/" + filename + "." + self.extension, "wb") as file:
				file.write(self.fullFile)
			self.com.disable()
	
	def print_progress_bar (self, packageNumber, totalOfPackages, tp, oh, message):
		progressBar(packageNumber, totalOfPackages, tp, oh, message)

	def close_connection(self):
		print("-----------------")
		print("connection closed")
		print("-----------------")
		self.send_response(bytes([0x05]))
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
serialName = serial.tools.list_ports.comports()[0][0]
controlerServer = ControlerServer(serialName, 1)

print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")
