import datetime
import random
import queue
import threading
from server_helpers.TempID import TempID

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
