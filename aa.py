import curses
from math import floor
from time import sleep

def progressBar(current_package, totalPacotes, Throughput, Overhead, message):
	a = (current_package/totalPacotes)*100
	aa = floor(a)
	stdscr.addstr(0,   0,  "Current Package"                                     )
	stdscr.addstr(0, 115,  "Total of Packages"                                 )
	stdscr.addstr(1,   0, f"{current_package}"                                   )
	stdscr.addstr(1, 125, f"{totalPacotes}"                                    )
	stdscr.addstr(1,  13,  "[" + "#"*aa + "-"*(100-aa) + "]"                    )    
	stdscr.addstr(3,   0, f"Throughput: {round(Throughput, 4)} packages/second")
	stdscr.addstr(4,   0, f"Overhead  : {Overhead} PackageSize/PayLoadSize"    )
	stdscr.addstr(5,   0, f"Message   : {message}")
	stdscr.refresh()

	stdscr.clear()

	if current_package==totalPacotes-1:
		print(f"""ActualPackage                                                                                                      Total of Packages
{current_package+1}          [####################################################################################################]          {totalPacotes}

Throughput: {Throughput} packages/second
Overhead  : {Overhead} PackageSize/PayLoadSize
Message   : {message}""")

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
# curses.curs_set(True)
total = 1000
for e in range(total):
	progressBar(e, total, 0, 0, 0)
	sleep(0.01)