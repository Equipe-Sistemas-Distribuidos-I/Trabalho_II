# import grpc
import devices_pb2
import devices_pb2_grpc
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


class gateway_server_skt():
    def __init__(self , server_Name = gethostbyname(gethostname()) , server_Port = 50051 , max_conections = 5) -> None:
        # server_Name = '/path/to/my/socket'
        self.skt_Server  = socket(AF_INET , SOCK_STREAM)
        self.skt_Server.bind((server_Name , server_Port))
        self.skt_Server.listen(max_conections)
        self.devices = {}
        self.channels = {}

        print("Server Ligado ", server_Name )

    #USANDO SOCKETS :

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


    #USANDO GRPC :

    def find_grpc_connections(self , timer = 3) :
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

            print("Iniciando a busca grpc em multicast")

            raw_data, address = sock.recvfrom(1024)
            # print(sock.recvfrom(1024))

            data = devices_pb2.device_discover()
            data.ParseFromString(raw_data)
            
            print(f"Recebido: \n{data} \nde {address}")
            self.channels[data.name] = data

            if (time.time() - start_time) > timer :
                    print("Busca por devices grpc encerrada")
                    break
            
        for i in self.channels.values() :
            channel = grpc.insecure_channel(f"localhost:{i.port}")
            # aux = socket(AF_INET , SOCK_STREAM)
            # aux.connect((address[0], i.port ))
            self.channels[i.name] = channel #aux 
            

        # self.devices = { i.name: socket(AF_INET , SOCK_STREAM).connect((address[0], i.port )) for i in self.devices.values() }
        print(self.devices)

    def handle_grpc_request(self , connection , addr):
        print("[GATEWAY : NOVA Conexão..]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.use_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                print(request)

                if request.service  == "ar_condicionado" :
                    self.__handle_grpc_method_type(data , request , request.service , connection)
                elif request.service  == "lampada" :
                    self.__handle_grpc_method_type(data , request , request.service , connection)
                elif request.service  == "geladeira" :
                    self.__handle_grpc_method_type(data , request , request.service , connection)

    def __handle_grpc_method_type(self , data , request , type , connection ):

        if request.method == f"{type}_status"  :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            """self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)"""
            stub = None
            if type == "ar_condicionado" :
                stub = devices_pb2_grpc.ar_condicionadoStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_status( data )
            elif type == "lampada" :
                stub = devices_pb2_grpc.lampadaStub( self.channels[ request.device_name ] )
                response = stub.lampada_status( data )
            elif type == "geladeira" :
                stub = devices_pb2_grpc.geladeiraStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_status( data )
            
            # response = stub.SayHello(meuservico_pb2.HelloRequest(name="Mundo"))
            print("Resposta do servidor:", response )
            # stub = self.devices[request.device_name]
            
        elif request.method == f"{type}_on"  :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            """self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)"""

            stub = None
            if type == "ar_condicionado" :
                stub = devices_pb2_grpc.ar_condicionadoStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_on( data )
            elif type == "lampada" :
                stub = devices_pb2_grpc.lampadaStub( self.channels[ request.device_name ] )
                response = stub.lampada_on( data )
            elif type == "geladeira" :
                stub = devices_pb2_grpc.geladeiraStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_on( data )
            
            # response = stub.SayHello(meuservico_pb2.HelloRequest(name="Mundo"))
            print("Resposta do servidor:", response )

        elif request.method == f"{type}_off" :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            # data.new_temp = int(request.args)

            """self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)"""

            stub = None
            if type == "ar_condicionado" :
                stub = devices_pb2_grpc.ar_condicionadoStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_off( data )
            elif type == "lampada" :
                stub = devices_pb2_grpc.lampadaStub( self.channels[ request.device_name ] )
                response = stub.lampada_off( data )
            elif type == "geladeira" :
                stub = devices_pb2_grpc.geladeiraStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_off( data )
            
            # response = stub.SayHello(meuservico_pb2.HelloRequest(name="Mundo"))
            print("Resposta do servidor:", response )

        elif request.method == f"{type}_temp" :
            data = devices_pb2.info_request()
            data.service  = request.service
            data.method   = request.method
            data.name     = request.device_name
            data.new_temp = int(request.args)

            """self.devices[request.device_name].send(data.SerializeToString())
            data = self.devices[request.device_name].recv(1024)

            connection.send(data)"""

            stub = None
            if type == "ar_condicionado" :
                stub = devices_pb2_grpc.ar_condicionadoStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_temp( data )
            # elif type == "lampada" :
            #     stub = devices_pb2_grpc.lampadaStub( self.channels[ request.device_name ] )
            #     response = stub.lampada( data )
            elif type == "geladeira" :
                stub = devices_pb2_grpc.geladeiraStub( self.channels[ request.device_name ] )
                response = stub.ar_condicionado_temp( data )
            
            # response = stub.SayHello(meuservico_pb2.HelloRequest(name="Mundo"))
            print("Resposta do servidor:", response )

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

    def start_grpc_connections(self):
        print("[Tentando Estabelecer conexões grpc...]")
        while True:
            
            client , addr = self.skt_Server.accept()
            
            td = threading.Thread(target = self.handle_grpc_request , args=(client, addr))
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

