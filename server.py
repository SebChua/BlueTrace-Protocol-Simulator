import sys
import socket
from DataManager import DataManager
from server_helpers.LoginManager import LoginManager, LoginStatus

if len(sys.argv) != 3:
    print('Usage: {} server_port block_duration'.format(sys.argv[0]))
    exit()

server_IP = 'localhost'
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])   # Duration (seconds) user will be blocked after 3 unsuccessful login attempts

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_IP, server_port))
server_socket.listen(5)

login_manager = LoginManager(block_duration)

print('Server listening for connections.')

while True:
    client_socket, address = server_socket.accept()
    received_data = client_socket.recv(1024)
    while received_data:
        credentials = DataManager.decode_object(received_data)
        print('Received credentials.')
        print(credentials)
        logged_in_status = login_manager.login(credentials)
        client_socket.send(DataManager.encode_object(logged_in_status))

        # Listen for more attempts from the client
        received_data = client_socket.recv(1024)
