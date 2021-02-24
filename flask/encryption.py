from Crypto import Random
from Crypto.Cipher import AES
import os
import os.path
from os import listdir
from os.path import isfile, join
import time
from glob import glob


class Encryptor:
    def __init__(self, key):
        self.key = key

    def pad(self, s):
        return s + b"\0" * (AES.block_size - len(s) % AES.block_size)

    def encrypt(self, message, key, key_size=256):
        message = self.pad(message)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(message)

    def encrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext, self.key)
        with open(file_name + ".enc", 'wb') as fo:
            fo.write(enc)
        os.remove(file_name)

    def decrypt(self, ciphertext, key):
        iv = ciphertext[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext[AES.block_size:])
        return plaintext.rstrip(b"\0")

    def decrypt_file(self, file_name):
        with open(file_name, 'rb') as fo:
            ciphertext = fo.read()
        dec = self.decrypt(ciphertext, self.key)
        with open(file_name[:-4], 'wb') as fo:
            fo.write(dec)
        os.remove(file_name)

    def getAllFilestoEncrypt(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path+"/people"
        dirs = []
        for dirName, subdirList, fileList in os.walk(dir_path):
            for fname in fileList:
                if (fname != 'data.txt.enc' and fname != '.DS_Store' and fname not in glob('*.enc')):
                    dirs.append(dirName + "/" + fname)
        return dirs

    def getAllFilestoDecrypt(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = dir_path+"/people"
        dirs = []
        for dirName, subdirList, fileList in os.walk(dir_path):
            for fname in fileList:
                if (fname != 'data.txt.enc' and fname != 'data.txt' and fname not in glob('*.jpg') and fname not in glob('*.jpeg') and fname != '.DS_Store'):
                    dirs.append(dirName + "/" + fname)
        return dirs

    def encrypt_all_files(self):
        dirs = self.getAllFilestoEncrypt()
        for file_name in dirs:
            self.encrypt_file(file_name)

    def decrypt_all_files(self):
        dirs = self.getAllFilestoDecrypt()
        for file_name in dirs:
            self.decrypt_file(file_name)

if __name__ == "__main__":
    key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
    enc = Encryptor(key)
    # clear = lambda: os.system('cls')
    def clear():
        os.system('clear')

    if os.path.isfile('people/data.txt.enc'):
        while True:
            password = str(input("Enter password: "))
            enc.decrypt_file("people/data.txt.enc")
            p = ''
            with open("people/data.txt", "r") as f:
                p = f.readlines()
            if p[0] == password:
                enc.encrypt_file("people/data.txt")
                break

        while True:
            clear()
            choice = int(input(
                "1. Encrypt.\n2. Decrypt.\n3. Exit.\n"))
            clear()
            if choice == 1:
                enc.encrypt_all_files()
                # enc.encrypt_file(str(input("Enter name of file to encrypt: ")))
            elif choice == 2:
                enc.decrypt_all_files()
                # enc.decrypt_file(str(input("Enter name of file to decrypt: ")))
            elif choice == 3:
                exit()
            else:
                print("Please select a valid option!")

    else:
        while True:
            clear()
            password = str(input("Setting up. Enter a password that will be used for decryption: "))
            repassword = str(input("Confirm password: "))
            if password == repassword:
                break
            else:
                print("Passwords Mismatched!")
        f = open("people/data.txt", "w+")
        f.write(password)
        f.close()
        enc.encrypt_file("people/data.txt")
        print("Program restart required to complete the setup")
        time.sleep(15)