# import grpc
import devices_pb2
# import ar_condicionado_pb2_grpc
from concurrent import futures
from socket import *
import threading
from abc import ABC, abstractmethod
from constants import *
import struct
import time
from devices import *
# import multiprocessing as mp

import subprocess
import platform
"""
class device_interface(ABC):

    @abstractmethod
    def handle_request(self , connection , addr):
        pass

"""
"""OS DISPOSITIVOS SERÃO TODOS SERVIDORES , ENQUANTO O GATEWAY É TANTO CLIENTE DOS DISPOSITIVOS , QUANTO SERVIDOR
DE QUEM QUEIRA SE CONECTAR AO SISTEMA SERVINDO COMO A INTERFACE COM O MUNDO EXTERNO"""
"""
class ar_condicionado(device_interface):

    def __init__(self , name : str ="Brastemp_Eletrolux" , on: bool = False, temperature : int = 20  ,
                 server_Name = gethostbyname(gethostname()) , server_Port = 50051  ) -> None:
        super(ar_condicionado , self).__init__()
        self.name = name
        self.temperature = temperature
        self.on = on
        
        self.server_Port = server_Port
        self.skt_Server  = socket( AF_INET , SOCK_STREAM )
        self.skt_Server.bind(( server_Name , server_Port ))
        self.skt_Server.listen(5)
        
        
        print("Server Ligado ", server_Name )
    
    def tcp_connect(self , timeout = 6):
        client , addr = None , None
        print("ar_condicionado aberto a novas conexões TCP")
        while True :
            try :
                self.skt_Server.settimeout(timeout)

                client , addr = self.skt_Server.accept()

                mp = threading.Thread(target = self.handle_request , args=(client, addr))
                mp.start()

            except error as e:
                # Tratamento de exceção para liberar a thread em caso de interrupção
                print("tempo de espera por novas conexões em ar_condicionado encerrado ")
                
                return
            

    def send_info_2_multicast(self , timer = 10):
        # Criação de um socket UDP
        sock = socket( AF_INET , SOCK_DGRAM , IPPROTO_UDP )

        # Vincula o socket a um endereço e porta local
        # server_address = ("", port )
        # sock.bind( server_address )

        # Configura o socket para enviar dados para o grupo multicast
        group = inet_aton( multicast_group )
        mreq = struct.pack( "4sL", group , INADDR_ANY )
        sock.setsockopt( IPPROTO_IP , IP_ADD_MEMBERSHIP, mreq )
        # sock.setsockopt( IPPROTO_IP , IP_MULTICAST_TTL , 8 )
        
        try:
            print("O dispositivo iniciou a tentativa de estabelecer conecção via multicast e permanecerá tentando pelos próximos 1 minuto")
            # message = f"{self.server_Port} , ar_condicionado , {self.name}"
            message = devices_pb2.device_discover()
            message.name = self.name
            message.port = self.server_Port
            message.device_type = "ar_condicionado"

            start_time = time.time()
            while True:
                
                sock.sendto(message.SerializeToString() , (multicast_group, port))
                time.sleep(1)
                if (time.time() - start_time) > timer :
                    break
            print("Servidor multicast encerrado.")
        except KeyboardInterrupt:
            print("Servidor multicast encerrado.")
        finally:
            sock.close()
    def conect_in_localhost_devices(self , timer = 4):
        
        self.exit_thread = False
        td1 = threading.Thread(target= self.send_info_2_multicast , args=(timer,))
        td1.start()

        td2 = threading.Thread(target= self.tcp_connect , args=(timer,))
        td2.start()


    def handle_request(self , connection , addr):
        print("[NOVA Conexão em..  ar_condicionado ]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.info_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                
                if  request.service  == "ar_condicionado" and request.method == "ar_condicionado_status":
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature

                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_on"  :
                    self.on = True
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_off" :
                    self.on = False
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_temp" :
                    self.temperature = request.new_temp
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "close_connection" :
                    connection.close()
                    return
                else:
                    print("Serviço ou método desconhecido")

                # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
                
                connection.send(response.SerializeToString())
                # connection.close()
                # return

    def __str__(self) -> str:
        return f"ar_condicionado() : {self.name} , temperature : {self.temperature} , on : {self.on}"
    
"""
class gateway_server_skt():
    def __init__(self , server_Name = gethostbyname(gethostname()) , server_Port = 50051 , max_conections = 5) -> None:
        # server_Name = '/path/to/my/socket'
        self.skt_Server  = socket(AF_INET , SOCK_STREAM)
        self.skt_Server.bind((server_Name , server_Port))
        self.skt_Server.listen(max_conections)
        self.devices = {}

        print("Server Ligado ", server_Name )
    
    def find_devices(self , timer = 3) :
        # Criação de um socket UDP
        sock = socket(AF_INET, SOCK_DGRAM , IPPROTO_UDP)

        # Configura o socket para receber dados do grupo multicast
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL , 32) 
        sock.setsockopt(IPPROTO_IP, IP_MULTICAST_LOOP, 1)
        # sock.bind(("", port + rd.randint(1,13000)))
        sock.bind(("", port ))
        

        # Adiciona o cliente ao grupo multicast
        mreq = inet_aton(multicast_group) + inet_aton("0.0.0.0")
        sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)

        # sock.listen(2)
        start_time = time.time()
        while True:

            print("Iniciando a busca em multicast")

            raw_data, address = sock.recvfrom(1024)
            # print(sock.recvfrom(1024))

            data = devices_pb2.device_discover()
            data.ParseFromString(raw_data)
            
            print(f"Recebido: \n{data} \nde {address}")
            self.devices[data.name] = data

            if (time.time() - start_time) > timer :
                    print("Busca por devices encerrada")
                    break
            
        for i in self.devices.values() :
            aux = socket(AF_INET , SOCK_STREAM)
            aux.connect((address[0], i.port ))
            self.devices[i.name] = aux 

        # self.devices = { i.name: socket(AF_INET , SOCK_STREAM).connect((address[0], i.port )) for i in self.devices.values() }
        print(self.devices)
    def __handle_method_type(self , data , request , type , connection ):

        if request.method == f"{type}_status":
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)
            
        elif request.method == f"{type}_on"  :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)

        elif request.method == f"{type}_off" :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)

        elif request.method == f"{type}_temp" :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            data.new_temp = int(request.args)

            self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)
        elif  request.method == "close_connection" :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name

            self.devices[request.device_name].send(data.SerializeToString())
            self.devices[request.device_name].close()
            # self.devices[request.device_name] = "Conexão fechada"
            # connection.close()
        elif request.service == "close":

            connection.close()
            return
        else:
            print("Serviço ou método desconhecido")

    def handle_request(self , connection , addr):
        print("[GATEWAY : NOVA Conexão..]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.use_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                print(request)

                if request.service  == "ar_condicionado" :
                    self.__handle_method_type(data , request , request.service , connection)
                elif request.service  == "lampada" :
                    self.__handle_method_type(data , request , request.service , connection)
                elif request.service  == "geladeira" :
                    self.__handle_method_type(data , request , request.service , connection)
                
                """
                if  request.service  == "ar_condicionado" and request.method == "ar_condicionado_status":
                    
                    data = devices_pb2.info_request()
                    data.service  = request.service
                    data.method   = request.method
                    data.name     = request.device_name
                    # data.new_temp = int(request.args)

                    self.devices[request.device_name].send(data.SerializeToString())
                    data = self.devices[request.device_name].recv(1024)

                    connection.send(data)
                    
                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_on"  :
                    data = devices_pb2.info_request()
                    data.service  = request.service
                    data.method   = request.method
                    data.name     = request.device_name
                    # data.new_temp = int(request.args)

                    self.devices[request.device_name].send(data.SerializeToString())
                    data = self.devices[request.device_name].recv(1024)

                    connection.send(data)

                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_off" :
                    data = devices_pb2.info_request()
                    data.service  = request.service
                    data.method   = request.method
                    data.name     = request.device_name
                    # data.new_temp = int(request.args)

                    self.devices[request.device_name].send(data.SerializeToString())
                    data = self.devices[request.device_name].recv(1024)

                    connection.send(data)

                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_temp" :
                    data = devices_pb2.info_request()
                    data.service  = request.service
                    data.method   = request.method
                    data.name     = request.device_name
                    data.new_temp = int(request.args)

                    self.devices[request.device_name].send(data.SerializeToString())
                    data = self.devices[request.device_name].recv(1024)

                    connection.send(data)
                elif request.service == "ar_condicionado" and request.method == "close_connection" :
                    data = devices_pb2.info_request()
                    data.service  = request.service
                    data.method   = request.method
                    data.name     = request.device_name

                    self.devices[request.device_name].send(data.SerializeToString())
                    self.devices[request.device_name].close()
                    # self.devices[request.device_name] = "Conexão fechada"
                    # connection.close()
                elif request.service == "close":

                    connection.close()
                    return
                else:
                    print("Serviço ou método desconhecido")
                """


                """print(f"O data recebido foi :\n{data}\n\nO request do data ficou :\n{request.name}")
                response = ar_condicionado_pb2.ar_condicionado_info()
                response.temperature = 3
                response.on = True
                # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
                
                connection.send(response.SerializeToString())
                connection.close()
                return"""

    def start_server(self):
        # listen()
        print("[Server Ouvindo...]")
        while True:
            
            client , addr = self.skt_Server.accept()
            
            td = threading.Thread(target = self.handle_request , args=(client, addr))
            td.start()

def main():
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(("localhost", 50051))
    server_socket.listen(5)

    print("Servidor socket em execução...")

    while True:
        client_socket, _ = server_socket.accept()
        data = client_socket.recv(1024)
        
        request = ar_condicionado_pb2.info_request()
        request.ParseFromString(data)
        print(f"O data recebido foi :\n{data}\n\nO request do data ficou :\n{request.name}")
        response = ar_condicionado_pb2.ar_condicionado_info()
        response.temperature = 3
        response.on = True
        # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
        
        client_socket.send(response.SerializeToString())
        client_socket.close()

if __name__ == "__main__":
    # main()
    # ar = ar_condicionado(server_Port = 50370)
    # ar.open_multicast_connection()

    # gateway = gateway_server_skt()
    # gateway.find_devices()

    pass

