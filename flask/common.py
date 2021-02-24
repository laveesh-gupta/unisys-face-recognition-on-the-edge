import face_recognition
from os import listdir
from os.path import isfile, join
from glob import glob
from encryption import Encryptor
import time

def get_users():

    known_names=[]
    known_encods=[]

    key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
    enc = Encryptor(key)
    enc.decrypt_all_files()

    for i in glob("people/*.jpg"):
        img = face_recognition.load_image_file(i)
        encoding = face_recognition.face_encodings(img)[0]
        known_encods.append(encoding)
        known_names.append(i[7:-4])

    enc.encrypt_all_files()

    return known_names, known_encods



