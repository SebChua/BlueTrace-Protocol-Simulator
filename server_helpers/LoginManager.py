import time
import enum

MAX_ATTEMPTS = 3

class LoginManager:
    def __init__(self, blocking_duration):
        # Keeps track of the username, num of attempts, and last attempted time
        self.attempts = {}
        self.logged_in = {}
        self.blocking_duration = blocking_duration

    def can_login(self, username):
        '''Checks if a username is blocked from logging in'''
        if username not in self.attempts:
            return True

        attempt_record = self.attempts.get(username)
        if attempt_record[0] < MAX_ATTEMPTS:
            return True

        if int(time.time() - attempt_record[1]) > self.blocking_duration:
            # If last accessed time is longer than the blocking duration
            self.attempts.pop(username, None)
            return True

        print(f'Account: {username} is blocked due to too many attempts')
        return False
    
    def login(self, credentials, addr):
        '''Checks if the credentials match a valid user'''
        if not self.can_login(credentials['username']):
            return LoginStatus.BLOCKED

        # Open credentials.txt and check for any matching lines
        credential_file = open('credentials.txt', 'r')
        for valid_credential in credential_file:
            username, password = valid_credential.split()
            if credentials['username'] == username:
                if credentials['password'] == password:
                    # Successful login
                    if username in self.attempts:
                        # Clear the attempts
                        del self.attempts[username]
                    
                    self.logged_in[addr] = username
                    return LoginStatus.SUCCESS
                
                # Matched a valid user but wrong password
                attempt_record = self.attempts.get(username, (0, None))
                self.attempts[username] = (attempt_record[0] + 1, time.time())
                print(self.attempts)
                if self.attempts[username][0] == MAX_ATTEMPTS:
                    return LoginStatus.BLOCKING
                
                return LoginStatus.WRONGPASSWORD

        credential_file.close()
        return LoginStatus.NOMATCH

    def logout(self, addr):
        self.logged_in.pop(addr)

class LoginStatus(str, enum.Enum):
    SUCCESS = 'Welcome to the BlueTrace Simulator.'
    NOMATCH = 'No account connected to the given username.'
    WRONGPASSWORD = 'Invalid Password. Please try again.'
    BLOCKING = 'Invalid Password. Your account has been blocked. Please try again later.'
    BLOCKED = 'Your account has been blocked due to multiple attempts. Please try again later.'