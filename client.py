import sys
import os
import socket
import datetime
import threading
from DataManager import DataManager
from server_helpers import LoginStatus, TempIDManager

MAX_DELAY = 5

if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_ip = 'localhost'             # Assume localhost for assignment for client IP
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients

# Setup TCP socket to communicate with server
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp_socket.settimeout(MAX_DELAY)
client_tcp_socket.connect((server_IP, server_port))

# Setup UDP socket for P2P Beaconing
client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_udp_socket.bind((client_udp_ip, client_udp_port))

def login():
    '''Attempt client login to server'''
    global client_tcp_socket

    while True:
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
            return username
        elif login_response == LoginStatus.BLOCKED:
            # Username has been blocked and prompt should exit
            exit()

def listen(username):
    '''Listen for command inputs from the user'''
    while True:
        command = input('> ').split()

        if command[0] == 'logout':
            client_tcp_socket.send('logout'.encode('utf-8'))
            exit()
        # TODO: CHANGE COMMAND NAME LATER to Download_tempID
        elif command[0] == 'download':
            client_tcp_socket.send('Download_tempID'.encode('utf-8'))
            tempID_entry = client_tcp_socket.recv(1024).decode('utf-8')
            tempID = TempIDManager.parse_tempID_entry(tempID_entry)
            print(f'TempID: {tempID.tempID}')

        # TODO: CHANGE COMMAND NAME LATER to Upload_contact_log
        elif command[0] == 'upload':
            client_tcp_socket.send('Upload_contact_log'.encode('utf-8'))

            # Inform server first the size of the contact log to be sent
            contactlog = f'{username}_contactlog.txt'
            log_size = os.stat(contactlog).st_size
            client_tcp_socket.send(str(log_size).encode('utf-8'))

            # Upload contact log to server
            with open(contactlog, 'r') as f:
                log_contents = f.read()
                client_tcp_socket.send(log_contents.encode('utf-8'))
                print(log_contents)
        elif command[0] == 'Beacon':
            if len(command) != 3:
                print('Usage: Beacon <destination IP> <destination port>')
                continue
            
            destIP = command[1]
            destPort = int(command[2])
            dest = (destIP, destPort)
            client_tcp_socket.send('Download_tempID'.encode('utf-8'))
            tempID_entry = client_tcp_socket.recv(1024)
            print(tempID_entry.decode('utf-8'))
            client_udp_socket.sendto(tempID_entry, dest)
        else:
            print('Error, invalid comm  and. The available commands are:')
            print(' - Download_tempId: Downloads tempID from server')
            print(' - Upload_contact_log: Upload contact logs to the server')
            print(' - logout: Logs out fromm the server')
            print(' - Beacon <destination IP> <destination port>: Send a beacon to another user.')

def beacon_listen():
    global client_udp_socket
    while True:
        # Listen for any received beacons from peers
        beacon = client_udp_socket.recvfrom(1024)
        curr_time = datetime.datetime.now()
        print(f'Received Beacon at {curr_time}:')
        print(beacon)

        tempID = TempIDManager.parse_tempID_entry(beacon)
        if tempID.created <= curr_time <= tempID.expiry:
            print('Received a VALID beacon.')
        else:
            print('Beacon is INVALID')


def start():
    username = login()
    if username:
        listen(username)
        beacon_thread = threading.Thread(target=beacon_listen, daemon=True)
        beacon_thread.start()

start()


