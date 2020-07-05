import sys
import socket
import threading
from DataManager import DataManager
from server_helpers.LoginManager import LoginManager, LoginStatus

# Server Initialisation
if len(sys.argv) != 3:
    print('Usage: {} server_port block_duration'.format(sys.argv[0]))
    exit()

server_IP = 'localhost'
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])   # Duration (seconds) user will be blocked after 3 unsuccessful login attempts

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_IP, server_port))
login_manager = LoginManager(block_duration)

def start_server():
    global server_socket
    server_socket.listen()
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
        client_thread.start()

def handle_client(client_socket, addr):
    received_data = client_socket.recv(1024)
    while received_data:
        credentials = DataManager.decode_object(received_data)
        print('Received credentials.')
        print(credentials)
        logged_in_status = login_manager.login(credentials)
        client_socket.send(DataManager.encode_object(logged_in_status))

        # Listen for more attempts from the client
        received_data = client_socket.recv(1024)

print('Server listening for connections.')
start_server()


    
