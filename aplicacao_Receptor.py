
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################


from enlace import *
import binascii

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


def main():
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()

    print("Comunicação inicializada")
    
    
    txSize = com.tx.getStatus()

    txLen, nRxLen = com.getData(2)
    txLen = int.from_bytes(txLen, 'big')


    rxBuffer, nRx = com.getData(txLen) 
    
    com.sendData(nRx.to_bytes(2, "big"))


    with open("received_image" + str(testNumber) + ".png", "wb") as image:
        image.write(rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
testNumber = 0
if __name__ == "__main__":
    # for e in range(10):
        # main()
        # testNumber += 1
    main()
