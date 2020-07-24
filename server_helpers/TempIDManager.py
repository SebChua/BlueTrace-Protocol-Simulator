import datetime
import random
import queue
import threading

def generate_tempID():
    '''Generates a random 20-byte string of numbers'''
    return ''.join(["{}".format(random.randint(0, 9)) for num in range(20)])

class TempID:
    def __init__(self, username, tempID=None, created=None, expiry=None):
        self.username = username
        self.tempID = tempID if tempID else generate_tempID()
        self.created = created if created else datetime.datetime.now()
        self.expiry = expiry if expiry else self.created + datetime.timedelta(minutes=15)

    def __repr__(self):
        createdDateStr = self.created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = self.expiry.strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.username} {self.tempID} {createdDateStr} {expiryDateStr}'
    
    def contactlog_entry(self):
        createdDateStr = self.created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = self.expiry.strftime('%Y-%m-%d %H:%M:%S')
        insertedDate = datetime.datetime.now()
        return f'{self.tempID} {createdDateStr} {expiryDateStr}'
    
    @staticmethod
    def parse(tempID_repr: str):
        '''Parses the __repr__ to produce TempID'''
        items = tempID_repr.split()
        username = items[0]
        tempID = items[1]
        createdDateStr = ' '.join(items[2:4])
        createdDate = datetime.datetime.strptime(createdDateStr, '%Y-%m-%d %H:%M:%S')
        expiryDateStr = ' '.join(items[-2:])
        expiryDate = datetime.datetime.strptime(expiryDateStr, '%Y-%m-%d %H:%M:%S')
        return TempID(username, tempID, createdDate, expiryDate)


class TempIDManager:
    def __init__(self):
        self.jobs = queue.Queue()

    def get_tempID(self, username):
        '''Generates a line entry for a user and tempID pairing and queues it to be written to file'''
        # Need to generate a new tempID for the user
        tempID = TempID(username)
        # Enqueue entry to be written to the file
        self.jobs.put(repr(tempID))
        return tempID

    def get_username(self, tempID):
        '''Maps a tempID to a username'''
        with open('tempIDs.txt') as f:
            for entry in f:
                entry = TempID.parse(entry)
                if tempID == entry.tempID:
                    return entry.username
                    # expiryDateStr = ' '.join(entry_items[-2:])
                    # expiryDate = datetime.datetime.strptime(expiryDateStr, '%Y-%m-%d %H:%M:%S')
                    # if datetime.datetime.now() < expiryDate:
                    #     # Found a valid tempID for the user
                    #     return entry_items[0]
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
            with open('tempIds.txt', 'a') as f:
                f.write(entry + '\n')
            
            self.jobs.task_done()
