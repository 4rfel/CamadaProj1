import subprocess
from time import sleep
from math import floor
import random

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

# print(serial.tools.list_ports.comports()[0][0])

# sleep(10)

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

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
totalPacotes = random.randint(10, 1000)
throughput = random.randint(10, 1000)
overhead = random.randint(1,200)/100
message = str(bytes([0x05])).split("'")[1].replace("\\", "0")
print(str(bytes([0x05])))
for pacoteAtual in range(totalPacotes):
    sleep(0.01)
    progressBar(pacoteAtual, totalPacotes, throughput, overhead, message)
    



