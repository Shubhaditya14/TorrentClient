from collections import OrderedDict

TOKEN_INTEGER = b'i' #start of integer
TOKEN_DICT = b'd' #start of dict
TOKEN_LIST = b'l' #start of list
TOKEN_END = b'e' #end of int,dict,list
TOKEN_STRING_SEPARATOR = b':'#string starting after the number

class decoder:
    """
    Decodes a bencoded sequence of text
    """ 
    def __init__(self,data:bytes):
        if not isinstance(data, bytes):
            raise TypeError("Argument "data" must be of type bytes")
        self._data = data
        self._index = 0
    
    def decode(self):
        """
        Decodes the bencoded data and return the matching python object.
        """
        c = self._peek()
        if c is None:
            raise EOFError('Unexpected end-of-file')
        elif c == TOKEN_INTEGER:
            self._consume() #consume the token
            return self._decode_int()
        elif c == TOKEN_LIST:
            self._consume()
            return self._decode_list()
        elif c == TOKEN_DICT:
            self._consume()
            return self._decode_dict()
        elif c == TOKEN_END:
            return None
        elif c == b'01234567899':
             return self._decode_string()
        else:
            raise RuntimeError('Invalid token read at {0}'.format(
                str(self._index)))
        
    def _peek(self):
        """
        Return the next character from the bencoded data or None
        """
        if self._index + 1 >= len(self._data):
            return None
        return self._data[self._index:self._index + 1]
    
    def _consume(self) -> bytes:
        """
        Read (and therefore consume) the next character from the data
        """
        self._index += 1

    def _read(self, length: int) -> bytes:
        """
        Read the `length` number of bytes from data and return the result
        """
        if self._index + length > len(self._data):
            raise IndexError('Cannot read {0} bytes from current position {1}'
                             .format(str(length), str(self._index)))
        res = self._data[self._index:self._index+length]
        self._index += length
        return res
    
    def _read_until(self, token : bytes):
        """
        Read from the bencoded data until the given token is found and return
        the characters read.
        """
        try:
            occurrence = self._data.index(token, self._index)
            result = self._data[self._index:occurrence]
            self._index = occurrence + 1
            return result
        except ValueError:
            raise RuntimeError('Unable to find token {0}'.format(
                str(token)))
        
    def _decode_int(self):
        return int(self._read_until(TOKEN_END))
    
    def _decode_list(self):
        res = []
        while self._data[self._index: self._index+1] != TOKEN_END:
            res.append(self.decode())
        self._consume() #the end token
        return res
    
    def _decode_dict(self):
        res = OrderedDict()
        while self._data[self._index: self._index + 1] != TOKEN_END:
            key = self.decode()
            obj = self.decode()
            res[key] = obj
        self._consume()  # The END token
        return res

    def _decode_string(self):
        bytes_to_read = int(self._read_until(TOKEN_STRING_SEPARATOR))
        data = self._read(bytes_to_read)
        return data
    
    

    

