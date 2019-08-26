from tkinter import Tk, filedialog
from enlace import enlace
import serial
from classControlerClient import ControlerClient

serialName = serial.tools.list_ports.comports()[0][0]

# com = enlace(serialName)
# com.enable()

root = Tk()
root.withdraw()

filepath = filedialog.askopenfilename()

controlerClient = ControlerClient(filepath=filepath, serial=serialName)

# controlerServer = ControlerServer()
print("-------------------------")
print("Comunicação encerrada")
print("-------------------------")
print("")