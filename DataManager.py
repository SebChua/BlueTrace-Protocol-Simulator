import json

# Helper classes to encode and decode objects to be sent over the socket connection
class DataManager:
    @staticmethod
    def encode_object(obj):
        '''Encode a JSON object into utf-8'''
        return json.dumps(obj).encode('utf-8')

    @staticmethod
    def decode_object(obj):
        '''Decode utf-8 into a JSON object'''
        return json.loads(obj.decode('utf-8'))