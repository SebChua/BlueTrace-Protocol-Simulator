import sys
import socket
from DataManager import DataManager

if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients

# Setup TCP socket to communicate with server
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp_socket.connect((server_IP, server_port))

client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


username = input('> Username: ')
password = input('> Password: ')
credentials = {
    'username': username,
    'password': password
}
client_tcp_socket.send(DataManager.encode_object(credentials))


client_tcp_socket.close()
client_udp_socket.close()


