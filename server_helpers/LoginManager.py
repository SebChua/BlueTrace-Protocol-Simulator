import time

MAX_ATTEMPTS = 3

class LoginManager:
    def __init__(self, blocking_duration):
        # Keeps track of the username, num of attempts, and last attempted time
        self.attempts = {}
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

        print('Account: {} is blocked due to too many attempts', username)
        print(self.attempts)
        return False
    
    def login(self, credentials):
        '''Checks if the credentials match a valid user'''
        if not self.can_login(credentials['username']):
            return None

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
                    return credentials
                
                # Matched a valid user but wrong password
                attempt_record = self.attempts.get(username, (0, None))
                self.attempts[username] = (attempt_record[0] + 1, time.time())

        print(self.attempts)
        credential_file.close()
        return None