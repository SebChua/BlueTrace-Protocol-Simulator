import datetime
import random
import queue
import threading

class ContactLogManager:
    def __init__(self):
        self.jobs = queue.Queue()

    