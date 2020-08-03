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

class Server:
    def __init__(self, server_IP, server_port, block_duration):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((server_IP, server_port))

        # Helper classes to handle login and tempIDs
        self.login_manager = LoginManager(block_duration)
        self.id_manager = TempIDManager()
        self.id_manager.listen()
    
    def start(self):
        '''Start the server'''
        self.socket.listen()
        print('> Server listening for connections.')
        while True:
            conn, addr = self.socket.accept()
            client_thread = threading.Thread(target=self.handle_login, args=(conn, addr), daemon=True)
            client_thread.start()

    def handle_login(self, conn, addr):
        '''Handle a client connection's attempt to login'''
        received_data = conn.recv(1024)
        while received_data:
            credentials = DataManager.decode_object(received_data)
            logged_in_status = self.login_manager.login(credentials, addr)
            conn.send(DataManager.encode_object(logged_in_status))
            
            if logged_in_status == LoginStatus.SUCCESS:
                # Client logged in - listen for requests from the client
                print(f'[{addr}, {credentials["username"]}]: Logged in.')
                self.handle_requests(conn, addr, credentials['username'])
            else:
                print(f'[{addr}, {credentials["username"]}]: Attempted login.')
            
            try:
                # Listen for more attempts from the client
                received_data = conn.recv(1024)
            except:
                # Connection has been closed due to logout
                received_data = None

    def handle_requests(self, conn, addr, username):
        '''Listen for and handle a client's requests'''
        data = conn.recv(20)
        while data:
            command = data.decode('utf-8')
            print(f'> [{addr}, {username}]: ' + command)
            if command == 'logout':
                self.login_manager.logout(addr)
                print(f'{username} logout')
                conn.close()
                break

            elif command == 'Download_tempID':
                tempID = self.id_manager.get_tempID(username)
                print(f'> user: {username}')
                print(f'> TempID: {tempID.tempID}')
                conn.send(repr(tempID).encode('utf-8'))

            elif command == 'Upload_contact_log':
                self.contact_trace(conn, addr, username)

            # Listen for more requests
            data = conn.recv(20)

    def contact_trace(self, conn, addr, username):
        '''Map TempIDs in a user's contact log to actual usernames'''
        # Obtain client's contact log
        log_length = int(conn.recv(64).decode('utf-8'))
        contactlog = conn.recv(log_length).decode('utf-8')
        print(f'> Received contact log from {username}:')
        print(contactlog)

        print('> Contact Tracing from Contact Log')
        contact_trace = []
        log_entries = contactlog.split('\n')
        for entry in log_entries:
            # Map the tempIDs to valid usernames
            entry_items = entry.split()
            if entry_items:
                # Handle any empty lines in the entry
                tempID = entry_items[0]
                username = self.id_manager.get_username(tempID)
                if username:
                    # Form new contact tracing entry with username and tempID
                    entry_items[0] = username
                    entry_items.append(tempID)
                    contact_trace.append(' '.join(entry_items))
        print('\n'.join(contact_trace))

Server(server_IP, server_port, block_duration).start()




    
