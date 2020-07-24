import datetime
import random

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
