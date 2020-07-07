import datetime
import random
import queue
import threading

class TempIDManager:
    def __init__(self):
        self.jobs = queue.Queue()

    def get_tempID(self, username):
        '''Obtains an existing tempID or generates a new tempID for a user'''
        tempID = self.check_existing_entry(username)
        return tempID if tempID else self.generate_entry(username)

    def get_username(self, tempID):
        '''Maps a tempID to a username'''
        with open('tempIDs.txt') as f:
            for entry in f:
                entry_items = entry.split()
                entry_tempID = entry_items[1]
                if tempID == entry_tempID:
                    expiryDateStr = ' '.join(entry_items[-2:])
                    expiryDate = datetime.datetime.strptime(expiryDateStr, '%Y-%m-%d %H:%M:%S')
                    if datetime.datetime.now() < expiryDate:
                        # Found a valid tempID for the user
                        return entry_items[0]
        return None


    def generate_tempID(self):
        '''Generates a random 20-byte string of numbers'''
        return ''.join(["{}".format(random.randint(0, 9)) for num in range(20)])

    def generate_entry(self, username):
        '''Generates a line entry for a user and tempID pairing and queues it to be written to file'''
        tempID = self.generate_tempID()
        created = datetime.datetime.now()
        expiry = created + datetime.timedelta(minutes=15)
        createdDateStr = created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = expiry.strftime('%Y-%m-%d %H:%M:%S')

        entry = f'{username} {tempID} {createdDateStr} {expiryDateStr}'

        # Enqueue entry to be written to the file
        self.jobs.put(entry)
        return tempID

    def check_existing_entry(self, username):
        '''Checks if a valid tempID has been previously generated for the user'''
        with open('tempIDs.txt') as f:
            for entry in f:
                entry_items = entry.split()
                entry_username = entry_items[0]
                if username == entry_username:
                    expiryDateStr = ' '.join(entry_items[-2:])
                    expiryDate = datetime.datetime.strptime(expiryDateStr, '%Y-%m-%d %H:%M:%S')
                    if datetime.datetime.now() < expiryDate:
                        # Found a valid tempID for the user
                        return entry_items[1]
        return None

    def listen(self):
        '''Listen for any tempID entries that need to be written to tempIDs.txt'''
        file_writer_thread = threading.Thread(target=self.file_writer, daemon=True)
        file_writer_thread.start()

    def file_writer(self):
        '''Worker thread for writing tempIDs to the file'''
        while True:
            # Append entry to tempID file
            entry = self.jobs.get()
            f = open('tempIds.txt', 'a')
            f.write(entry + '\n')
            f.close()
            self.jobs.task_done()
    
    
