import sys
import socket
from DataManager import DataManager
from server_helpers.LoginManager import LoginStatus

MAX_DELAY = 5

def listen():
    while True:
        command = input('> ')

        if command == 'logout':
            client_tcp_socket.send('logout'.encode('utf-8'))
            exit()
        elif command == 'Download_tempID':
            client_tcp_socket.send('Download_tempID'.encode('utf-8'))
            tempID = client_tcp_socket.recv(1024).decode('utf-8')
            print(f'TempID: {tempID}')

        elif command == 'Upload_contact_log':
            client_tcp_socket.send('Upload_contact_log'.encode('utf-8'))
        else:
            print('Error, invalid command. The available commands are:')
            print(' - Download_tempId: Downloads tempmID from server')
            print(' - Upload_contact_log: Upload contact logs to the server')
            print(' - logout: Logs out fromm the server')


if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients

# Setup TCP socket to communicate with server
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp_socket.settimeout(MAX_DELAY)
client_tcp_socket.connect((server_IP, server_port))

# Setup UDP socket for P2P Beaconing
client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

logged_in = False

while not logged_in:
    username = input('> Username: ')
    password = input('> Password: ')
    credentials = {
        'username': username,
        'password': password
    }
    client_tcp_socket.send(DataManager.encode_object(credentials))

    login_response = client_tcp_socket.recv(1024).decode('utf-8').replace('"', '')
    print('>', login_response)

    if login_response == LoginStatus.SUCCESS:
        logged_in = True
        listen()
        break
    elif login_response == LoginStatus.BLOCKED:
        # Username has been blocked and prompt should exit
        exit()


