# pylint: disable=no-self-use
"""Sha Security"""
import hashlib
import random
import string
from uuid import uuid4

# SECURITY
class ShaSecurity:
    """Class for ShaSecurity"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor ShaSecurity class"""
    #     pass

    def string_to_sha_plus(self, data_str, add_str='1080PFULLHD20188'):
        """Convert String to Sha Plus"""
        # CONCAT add_str
        data_str = data_str + add_str
        # STRING TO SHA256
        secure_hash = hashlib.sha256(data_str.encode()).hexdigest()
        # UNICODE
        #secure_hash = self.unicodeConvert(secure_hash)

        return str(secure_hash)

    def string_to_sha(self, data_str):
        """Convert String to Sha"""
        # STRING TO SHA256
        secure_hash = hashlib.sha256(data_str.encode()).hexdigest()
        # UNICODE
        # secure_hash = self.unicodeConvert(secure_hash)

        return str(secure_hash)

    def random_str_generator(self, size=6, chars=string.ascii_uppercase):
        """Generate Random String"""
        # RANDOM STRING
        new_data = ''.join(random.choice(chars) for x in range(size))
        return new_data

    def create_random(self, var_type='str'):
        """Create Random"""

        if var_type == 'str':
            size = random.randint(1, 50)
            return self.random_str_generator(size)

        if var_type == 'int':
            return random.randint(1, 5000)

        return ''

    def generate_token(self, hyphens):
        """Generate Token"""

        if hyphens:

            return str(uuid4())

        return str(uuid4().hex)

if __name__ == '__main__':
    ShaSecurity()
    # print(shasecurity.string_to_sha_plus('penn'))
