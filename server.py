import sys
import socket
import threading
from DataManager import DataManager
from server_helpers import LoginManager, LoginStatus, TempIDManager

# Server Initialisation
if len(sys.argv) != 3:
    print('Usage: {} server_port block_duration'.format(sys.argv[0]))
    exit()

server_IP = 'localhost'
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])   # Duration (seconds) user will be blocked after 3 unsuccessful login attempts

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_IP, server_port))

# Helper classes to handle login and tempIDs
login_manager = LoginManager(block_duration)
id_manager = TempIDManager()
id_manager.listen()

def start_server():
    global server_socket
    server_socket.listen()
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_login, args=(conn, addr), daemon=True)
        client_thread.start()

def handle_client_login(conn, addr):
    global login_manager

    received_data = conn.recv(1024)
    while received_data:
        credentials = DataManager.decode_object(received_data)
        logged_in_status = login_manager.login(credentials, addr)
        conn.send(DataManager.encode_object(logged_in_status))
        
        if logged_in_status == LoginStatus.SUCCESS:
            break
        
        # Listen for more attempts from the client
        received_data = conn.recv(1024)

    # Client logged in - listen for requests from the client
    print(f'[{addr}, {credentials["username"]}]: Logged in.')
    handle_client_requests(conn, addr, credentials['username'])

def handle_client_requests(conn, addr, username):
    global id_manager

    data = conn.recv(20)
    while data:
        command = data.decode('utf-8')
        print(f'> [{addr}, {username}]: ' + command)
        if command == 'logout':
            login_manager.logout(addr)
            print(f'Logged out {username}.')
            conn.close()
            break
        elif command == 'Download_tempID':
            # Download temp id
            tempID = id_manager.get_tempID(username)
            print(f'TempID for {username}: {tempID}')
            conn.send(tempID.encode('utf-8'))
        elif command == 'Upload_contact_log':
            # Uploads the contact log
            pass

        # Listen for more requests
        data = conn.recv(20)

print('> Server listening for connections.')
start_server()


    
