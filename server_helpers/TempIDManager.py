import datetime
import random
import queue
import threading

class TempIDManager:
    def __init__(self):
        self.jobs = queue.Queue()

    def generate_tempID(self):
        '''Generates a random 20-byte string of numbers'''
        return ''.join(["{}".format(random.randint(0, 9)) for num in range(20)])

    def generate_entry(self, username):
        '''Generates a line entry for a user and tempID pairing'''
        created = datetime.datetime.now()
        expiry = created + datetime.timedelta(minutes=15)
        createdDateStr = created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = expiry.strftime('%Y-%m-%d %H:%M:%S')

        entry = f'{username} {self.generate_tempID()} {createdDateStr} {expiryDateStr}'

        # Enqueue entry to be written to the file
        self.jobs.put(entry)
        
        return entry

    def file_writer(self):
        while True:
            # Append entry to tempID file
            entry = self.jobs.get()
            f = open('testTempId.txt', 'a')
            f.write(entry + '\n')
            f.close()
            self.jobs.task_done()
    
    def listen(self):
        file_writer_thread = threading.Thread(target=self.file_writer, daemon=True)
        file_writer_thread.start()







TempIDManager().generate_entry('sebi')