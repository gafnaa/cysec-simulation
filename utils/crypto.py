import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

class PaddingOracle:
    def __init__(self, key=None):
        if key is None:
            key = b'YELLOW_SUBMARINE'
        self.key = key
        self.iv_size = AES.block_size
    
    def encrypt(self, plaintext):
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        iv = os.urandom(self.iv_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = pad(plaintext, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        combined = iv + ciphertext
        return base64.b64encode(combined).decode('ascii').replace('/', '_').replace('+', '-').replace('=', '')
    
    def decrypt(self, encrypted_data):
        try:
            encrypted_data = encrypted_data.replace('_', '/').replace('-', '+')
            while len(encrypted_data) % 4:
                encrypted_data += '='
            
            combined = base64.b64decode(encrypted_data)
            
            if len(combined) < self.iv_size:
                raise ValueError("Invalid ciphertext length")
            
            iv = combined[:self.iv_size]
            ciphertext = combined[self.iv_size:]
            
            if len(ciphertext) % AES.block_size != 0:
                raise ValueError("Invalid ciphertext block size")
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(ciphertext)
            
            plaintext = unpad(padded_data, AES.block_size)
            return plaintext.decode('utf-8')
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'padding' in error_msg:
                raise ValueError(error_msg)
            elif 'invalid' in error_msg and ('length' in error_msg or 'block' in error_msg):
                raise ValueError(error_msg)
            else:
                raise ValueError(error_msg)

oracle = PaddingOracle()