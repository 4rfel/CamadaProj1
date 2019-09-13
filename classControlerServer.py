from classPackage import PackageMounter, PackageDismounter, Head
from math import ceil, floor
from enlace import enlace
import subprocess
from time import sleep, time, localtime
from curses.textpad import Textbox, rectangle

from tkinter import filedialog, Tk


def install(name):
	subprocess.call(['pip', 'install', name])

def progressBar(current_package, totalPacotes, Throughput, Overhead, message):
	message = str(message).split("'")[1].replace("\\", "0")
	a = (current_package/totalPacotes)*100
	aa = floor(a)
	stdscr.addstr(0,   0,  "Current Package"                                      )
	stdscr.addstr(0, 115,  "Total of Packages"                                    )
	stdscr.addstr(1,   0, f"{current_package}"                                    )
	stdscr.addstr(1, 125, f"{totalPacotes}"                                       )
	stdscr.addstr(1,  13,  "[" + "█"*aa + "-"*(100-aa) + "]"                      )    
	stdscr.addstr(3,   0, f"Throughput   : {round(Throughput, 4)} bytes/second")
	stdscr.addstr(4,   0, f"Overhead     : {Overhead} PackageSize/PayLoadSize"    )
	stdscr.addstr(5,   0, f"Message Sent : {message}")

	stdscr.refresh()

	stdscr.clear()

	if current_package==totalPacotes-1:
		print(f"""ActualPackage                                                                                                      Total of Packages
{current_package+1}          [██████████████████████████████████████████████████████████████████████████████████████████████████]          {totalPacotes}

Throughput   : {Throughput} bytes/second
Overhead     : {Overhead} PackageSize/PayLoadSize
Message Sent : {message}""")
	
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
		self.throughput_timer = time()
		while self.current_package <= self.total_of_packages:
			# print("")
			# print(f"\rpacote atual: {self.current_package}  total de pacotes: {self.total_of_packages}  throughput: {self.throughput}  overhead: {self.overhead}", end="\r")
			print(f"pacote atual: {self.current_package}     total de pacotes: {self.total_of_packages}   throughput: {self.throughput}  overhead: {self.overhead}")

			self.timer_timeout_start = time()
			self.read_package()
			# self.com.rx.clearBuffer()
			# self.com.fisica.flush()
			print("")
			# progressBar(self.current_package, self.total_of_packages, self.throughput, self.overhead, self.msg)
			
		# filename = self.get_filename()
		filename = input("\nFilename: ")
		self.saveFile(filename)
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
		if not end:
			with open("server_log.txt", "a") as log:
				log.write(text)
		if end:
			with open("server_log.txt", "a") as log:
				log.write("====================================================================\n\n ")
	
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
				# print("\rsearching for connection", end="\r")
				print("searching for connection")				
				sleep(1)
			self.check_msg_0x01()
		else:
			self.current_package = 1
			self.send_response(bytes([0x02]))

			self.timer_timeout_start = time()

	def check_msg_0x01(self):
		head_bytes = self.com.getData(10+2)[0]
		print(f"head bytes: {head_bytes}")
		head = Head(head_bytes)
		msg = head.get_message()
		self.updateLog(msg, 2, "remetente", False, "recebido")
		server_number = head.get_server_number()
		self.total_of_packages = head.get_total_of_packages()
		self.message_interpreter(msg, server_number)

		extension_byte = head.get_extension()
		self.extension = self.extension_types_reverse[extension_byte]
		resto_size = head.get_payload_size()
		_ = self.com.getData(resto_size+4)

	
	def message_interpreter(self, msg, server_number):
		# print(f"message recived: {msg} \nserver number: {server_number}")
		if msg == 0x01:
			if server_number == self.server_number:
				self.ocioso = False

	def send_response(self, msg):
		print(f"msg sent: {msg}")
		self.msg = msg
		self.updateLog(msg, 2, "destinatario", False, "enviada")
#              packageNumber*3                         + msg*1 + totalPackages*3                           + extension*1   + servidor number*1 + payload size*1 = 10bytes
		head = self.current_package.to_bytes(3, "big") + msg   + self.total_of_packages.to_bytes(3, "big") + bytes([0x00]) + bytes([0x01])
		response_mounter = PackageMounter(head, bytes([0x00]))
		response = response_mounter.get_package()
		self.com.sendData(response)

	def check_timers(self):
		self.timer1_start = time()
		while self.com.rx.getIsEmpty():
			timer1_elapsed = time() - self.timer1_start
			timer_timeout_elapsed = time() - self.timer_timeout_start
			if timer_timeout_elapsed > 20:
				print("-----------------")
				print("TIMED OUT")
				print("-----------------")
				self.ocioso = True
				self.close_connection()
			elif timer1_elapsed > 2:
				self.com.fisica.flush()
				self.send_response(bytes([0x04]))
				self.msg = bytes([0x04])
				self.timer1_start = time()
				self.com.rx.clearBuffer()


	def read_package(self):
		self.check_timers()
		head_bytes, size = self.com.getDataTimer(10+2, self.timer_timeout_start, self.timer1_start)
		print(f"head bytes: {head_bytes}")
		if size == -1:
			self.close_connection()
		elif size == -2:
			self.msg = bytes([0x04])
			self.send_response(bytes([0x04]))
			self.com.fisica.flush()
			self.com.rx.clearBuffer()
			self.timer1_start = time()
		else:
			head = Head(head_bytes)
			self.updateLog(head.get_message(), 2, "remetente", False, "recebido")
			if head.get_current_package() == self.current_package:
				payload_size = head.get_payload_size()
				payload_EOP, size = self.com.getDataTimer(payload_size+4, self.timer_timeout_start, self.timer1_start)
				if size == -1:
					self.close_connection()
				elif size == -2:
					self.send_response(bytes([0x04]))
					self.msg = bytes([0x04])
					self.com.fisica.flush()
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
						self.throughput =  len(self.fullFile)/elapsed_throughput_timer
			else:
				self.send_response(bytes([0x06]))
				self.msg = bytes([0x06])
				self.com.fisica.flush()
				self.com.rx.clearBuffer()

			
		
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

# progressBar(1, 10, 1, 1, 1)
# sleep(50)
serialName = serial.tools.list_ports.comports()[0][0]
controlerServer = ControlerServer(serialName, 1)

print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")
