"""
person/binaries.py
"""

import base64
import pickle


class Binary:

    def str_to_binary(self, string) -> bytes:
        """create rows of binary data"""
        try:
            encoded_string = base64.b64encode(
                string.encode("utf-8")
            )  # .decode("utf-8")
            return encoded_string
        except UnicodeEncodeError as error:
            raise ValueError(f"Error encode: {error}")

    def binary_to_str(self, binary_str) -> str:
        """Transformation the base64's line to the  basis line"""
        try:
            decoded_bytes = base64.b64decode(binary_str)
            return decoded_bytes
        except (UnicodeDecodeError, base64.binascii.Error) as error:
            raise ValueError(f"Error decode: {error}")

    def object_to_binary(self, obj) -> bytes:
        """
        Here, is used library 'pickle' for a work with a binary and json data.
        Transformation object to the binary data"""
        return pickle.dumps(obj)

    def binary_to_object(self, binary_data) -> object:
        """Transformation binary of data to the object through the pickle"""
        try:
            return pickle.loads(binary_data)
        except pickle.PickleError as error:
            raise ValueError(f"Error deserializing object: {error}")
