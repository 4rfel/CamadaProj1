from tkinter import Tk, filedialog
from enlace import enlace
from Controlers import Client,Server

serialPort = "COM5"
root = Tk()
root.withdraw()

comm = enlace(serialPort)
comm.enable()

filepath = filedialog.askopenfilename()

server = Server(serialPort, comm)
# server = Server(serialPort)
# server.startThreads()


client = Client(filepath,serialPort, comm)
# client = Client(filepath,serialPort)
# client.startThreads()

client.sendPackage()
server.start()

comm.disable()