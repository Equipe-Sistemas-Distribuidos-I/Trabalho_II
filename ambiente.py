import time
from servidor import ar_condicionado , gateway_server_skt
# import threading

temperatura = 30
iluminado = False

#LOOP 

"""while True:
    #SIMULA O COMPORTAMENTO DE  TODOS OS DISPOSITIVOS :
    pass
    time.sleep(5)"""


gateway = gateway_server_skt()
gateway.find_devices()
gateway.start_server()

# td1 = threading.Thread(target = gateway.find_devices , args=())
# td1.start()

