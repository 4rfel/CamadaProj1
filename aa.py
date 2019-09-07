# from time import sleep
# total_pacotes = 100
# for e in range(total_pacotes):
    # print(f"\rpacote atual: {e}     total de pacotes: {total_pacotes}", end="\r")
    # print("\r[" + "#"*e + "-"*(100-e) + "]", end="\r")
#     sleep(0.2)
from time import localtime
time_var = localtime()
year = time_var.tm_year
month = time_var.tm_mon
day = time_var.tm_mday
hour = time_var.tm_hour
minuto = time_var.tm_min
sec = time_var.tm_sec
date = f"{year}/{month}/{day} --- {hour}:{minuto}:{sec}"
print(date)
# from math import ceil

# payload = bytes([0x00])*500

# eop = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])

# eop_stuffed =  bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2]) + bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])

# payload_total = payload.replace(eop, eop_stuffed, -1)
# package_size = len(payload)

# def mount_pakage(payload, atual, total, eop):    
#     tamanho_pacote = len(payload)
#     head = total.to_bytes(2, "big") + atual.to_bytes(2, "big") + bytes([tamanho_pacote]) + bytes([0xff])
#     pacote = head + payload + eop
#     return pacote

# lista_pacotes = []
# head_size = 6
# max_size = 128-head_size
# total_pacotes = ceil(len(payload_total)/max_size)
# print(total_pacotes)

# for i in range(total_pacotes):
#     payload = payload_total[i*max_size:(i+1)*max_size]
#     pacote = mount_pakage(payload, i, total_pacotes, eop)
#     lista_pacotes.append(pacote)

# print(lista_pacotes)
