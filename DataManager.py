import json

# Helper classes to encode and decode objects to be sent over 
# the socket connection
class DataManager:
    @staticmethod
    def encode_object(obj):
        return json.dumps(obj).encode('utf-8')

    @staticmethod
    def decode_object(obj):
        return json.loads(obj.decode('utf-8'))