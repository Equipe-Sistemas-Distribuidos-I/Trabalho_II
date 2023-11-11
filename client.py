import socket
import ar_condicionado_pb2

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 50051))

    request = ar_condicionado_pb2.info_request()
    request.name = "Brastemp-Eletrolux_X86"
    client_socket.send(request.SerializeToString())

    data = client_socket.recv(1024)
    response = ar_condicionado_pb2.ar_condicionado_info()
    response.ParseFromString(data)

    print("Resposta do servidor:  ", response.temperature)

if __name__ == "__main__":
    main()
