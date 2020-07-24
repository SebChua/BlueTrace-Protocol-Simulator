import sys
import os
import socket
import datetime
import time
import threading
from DataManager import DataManager
from server_helpers import LoginStatus, TempIDManager, TempID

MAX_DELAY = 5
CONTACT_LOG = 'z5161468_contactlog.txt'
LOG_EXPIRY = 180                        # Logs need to be cleared after 3 minutes

if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_ip = 'localhost'             # Assume localhost for assignment for client IP
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients

class Client:
    def __init__(self, server_IP, server_port, udp_IP, udp_port):
        # Setup socket for communicating with server
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.settimeout(MAX_DELAY)
        self.tcp_socket.connect((server_IP, server_port))

        # Setup socket for P2P Beaconing
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((udp_IP, udp_port))

    def start(self):
        login_result = self.login()
        if login_result == LoginStatus.BLOCKED:
            # Username has been blocked and prompt should exit
            exit()

        if login_result == LoginStatus.SUCCESS:
            beacon_thread = threading.Thread(target=self.beacon_listen, daemon=True)
            beacon_thread.start()
            self.listen()

    def login(self):
        '''Attempt login to server'''
        while True:
            username = input('> Username: ')
            password = input('> Password: ')
            credentials = {
                'username': username,
                'password': password
            }
            self.tcp_socket.send(DataManager.encode_object(credentials))

            login_response = self.tcp_socket.recv(1024).decode('utf-8').replace('"', '')
            print('>', login_response)

            if login_response == LoginStatus.SUCCESS:
                # User successfully logged in and identified
                self.username = username
                return login_response

        return login_response       
    
    def logout(self):
        self.tcp_socket.send('logout'.encode('utf-8'))
        exit()

    def listen(self):
        '''Listen for command inputs from the user'''
        while True:
            command = input('> ').split()

            if command[0] == 'logout':
                self.logout()
            
            # TODO: CHANGE COMMAND NAME LATER to Download_tempID
            elif command[0] == 'download':
                tempID = self.download_tempID()
                self.tempID = tempID.tempID
                print(f'TempID: {self.tempID}')

            # TODO: CHANGE COMMAND NAME LATER to Upload_contact_log
            elif command[0] == 'upload':
                self.upload_contact_log()
            
            elif command[0] == 'Beacon':
                if len(command) != 3:
                    print('Usage: Beacon <destination IP> <destination port>')
                    continue
                destIP = command[1]
                destPort = int(command[2])
                self.send_beacon(destIP, destPort)
            
            else:
                print('Error, invalid command. The available commands are:')
                print(' - Download_tempId: Downloads tempID from server')
                print(' - Upload_contact_log: Upload contact logs to the server')
                print(' - logout: Logs out from the server')
                print(' - Beacon <destination IP> <destination port>: Send a beacon to another user.')

    def download_tempID(self):
        '''Download tempID entry from the server'''
        self.tcp_socket.send('Download_tempID'.encode('utf-8'))
        response = self.tcp_socket.recv(1024).decode('utf-8')
        tempID_entry = TempID.parse(response)
        return tempID_entry

    def upload_contact_log(self):
        '''Upload client's contact log for contact tracing'''
        self.tcp_socket.send('Upload_contact_log'.encode('utf-8'))

        # Inform server first the size of the contact log to be sent
        self.check_contactlog()
        log_size = os.stat(CONTACT_LOG).st_size
        self.tcp_socket.send(str(log_size).encode('utf-8'))

        # Upload contact log to server
        with open(CONTACT_LOG, 'r') as f:
            log_contents = f.read()
            self.tcp_socket.send(log_contents.encode('utf-8'))
            print(log_contents)

    def send_beacon(self, destIP, destPort):
        '''Send Beacon to Peer specified by (destIP, destPort)'''
        tempID_entry = self.download_tempID()
        print(tempID_entry.contactlog_entry())
        self.udp_socket.sendto(repr(tempID_entry).encode('utf-8'), (destIP, destPort))

    def beacon_listen(self):
        '''Listen for any received beacons from peers'''
        while True:
            beacon, addr = self.udp_socket.recvfrom(1024)
            tempID = TempID.parse(beacon.decode('utf-8'))
            curr_time = datetime.datetime.now()

            print(f'[{addr}]: Received Beacon:')
            print(repr(tempID))
            print(f'Current time is: {curr_time}')

            if tempID.created <= curr_time <= tempID.expiry:
                # Write the beacon to the client's contact log
                print('The beacon is valid.')
                self.check_contactlog()
                with open(CONTACT_LOG, 'a') as f:
                    f.write(tempID.contactlog_entry() + '\n')

            else:
                print('The beacon is invalid.')
    
    def check_contactlog(self):
        '''Checks if contactlog is outdated'''
        if os.path.isfile(CONTACT_LOG):
            now = time.time()
            log_created_time = os.path.getctime(CONTACT_LOG)
            if now - log_created_time > LOG_EXPIRY:
                # Contact log expired and needs to be cleared
                os.remove(CONTACT_LOG)
        
        # If contact log is deleted, create a new empty one
        f = open(CONTACT_LOG, 'w')
        f.close()



Client(server_IP, server_port, client_udp_ip, client_udp_port).start()