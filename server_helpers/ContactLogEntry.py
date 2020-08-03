import datetime

class ContactLogEntry:
    def __init__(self, tempID, created, expiry, inserted=None):
        self.tempID = tempID
        self.created = created
        self.expiry = expiry
        self.inserted = inserted if inserted else datetime.datetime.now()
        self.bluetraceVersion = '1'

    def __repr__(self):
        '''Produces string representing a line entry in a contact log'''
        createdDateStr = self.created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = self.expiry.strftime('%Y-%m-%d %H:%M:%S')
        insertedDateStr = self.inserted.strftime('%Y-%m-%d %H:%M:%S')
        return f'{self.tempID} {createdDateStr} {expiryDateStr} {insertedDateStr} {self.bluetraceVersion}'

    def print(self):
        '''Prints out the entry excluding date inserted and the BlueTrace version number'''
        createdDateStr = self.created.strftime('%Y-%m-%d %H:%M:%S')
        expiryDateStr = self.expiry.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{self.tempID} {createdDateStr} {expiryDateStr}')

    def update_inserted_time(self):
        '''Updates inserted time property of the contact log entry'''
        self.inserted = datetime.datetime.now()
    
    @staticmethod
    def parse(contactlog_entry: str):
        '''Parses the __repr__ to produce ContactLogEntry'''
        items = contactlog_entry.split()
        tempID = items[0]
        createdDateStr = ' '.join(items[1:3])
        createdDate = datetime.datetime.strptime(createdDateStr, '%Y-%m-%d %H:%M:%S')
        expiryDateStr = ' '.join(items[3:5])
        expiryDate = datetime.datetime.strptime(expiryDateStr, '%Y-%m-%d %H:%M:%S')
        insertedDateStr = ' '.join(items[5:7])
        insertedDate = datetime.datetime.strptime(insertedDateStr, '%Y-%m-%d %H:%M:%S')
        return ContactLogEntry(tempID, createdDate, expiryDate, insertedDate)