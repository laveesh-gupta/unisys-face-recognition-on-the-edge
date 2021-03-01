from flask import Flask, render_template, request, jsonify
import face_recognition
import cv2
import numpy as np
from flask_socketio import SocketIO, emit
from livenessmodel import get_liveness_model
from common import get_users
import base64
import json
from engineio.payload import Payload
import time


Payload.max_decode_packets = 200


app = Flask(__name__)
socketio = SocketIO(app, logger=True)


@socketio.on('connect')
def test_connect():
    print("SOCKET CONNECTED")

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print("on_error: ", e, sep=' ')

@socketio.on_error('/login') # handles the '/chat' namespace
def error_handler_chat(e):
    print("on_error/l: ", e, sep=' ')

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print("default_error_handler: ", e, sep=' ')


i = 0

check_first = True

check_frame = True

# Get the liveness network
model = get_liveness_model()

# load weights into new model
model.load_weights("model/model.h5")
print("Loaded model from disk")

face_names = set()

# Initialize some variables
face_locations = []
face_encodings = []

# face_names = []
input_vid = []


@app.route('/')
def hello():
    return 'Hello, World!'

count = 0

@socketio.on('test liveness')
def test_liveness(data):
    global count
    # time.sleep(1)
    global input_vid, check_first, check_frame
    if check_first is True:
        check_frame = data['first_frame']
        if check_frame is True:
            check_first = False
            input_vid = []
            count = 0
    # global i
    # print(data['frameNo'])
    # print(data)
    # if(data['new_face'] == True):
    #     input_vid = []
    if check_frame is True:
        if len(input_vid) < 24:
            nparr = np.frombuffer(base64.b64decode(
                data['data'].split(',')[1]), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            liveimg = cv2.resize(frame, (100, 100))
            liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite(str(i) + '.jpg', liveimg)
            # i = i + 1
            input_vid.append(liveimg)
            print(len(input_vid))
        else:
            nparr = np.frombuffer(base64.b64decode(
                data['data'].split(',')[1]), np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            liveimg = cv2.resize(frame, (100, 100))
            liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
            # cv2.imwrite(str(i) + '.jpg', liveimg)
            # i = i + 1
            input_vid.append(liveimg)
            inp = np.array([input_vid[-24:]])
            inp = inp/255
            inp = inp.reshape(1, 24, 100, 100, 1)
            socketio.sleep(0)
            pred = model.predict(inp)
            input_vid = input_vid[-25:]
            print(pred[0][0])
            x = {'pred': str(pred[0][0])}
            emit('liveness prediction', json.dumps(x))
            if pred[0][0] <= .95:
                count = count + 1
                if count == 25:
                    check_frame = False
                    check_first = True
                    z={'stop': str(1)}
                    emit('stop', json.dumps(z))
            else:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(
                    small_frame, face_locations)
                # name = "Unknown"
                for face_encoding in face_encodings:
                    for ii in range(len(known_encods)):
                        # See if the face is a match for the known face(s)
                        match = face_recognition.compare_faces(
                            [known_encods[ii]], face_encoding)

                        if match[0]:
                            name = known_names[ii]
                            face_names.add(name)
                            break

                print('face_names', face_names, sep=' ')
                y = {'names': str(face_names)}
                emit('face names', json.dumps(y))
                check_first = True
                # input_vid = []



@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Read the users data and create face encodings
        global known_names, known_encods
        known_names, known_encods = get_users()
        return render_template('loginnew.html'), 200
    else:
        global input_vid
        process_this_frame = True

        # input_vid = []
        # frame = request.data
        # print('frame: ', frame, sep=' ')
        encoded_data = request.form['image']
        # print('encoded_data: ', encoded_data[:20], sep=' ')
        nparr = np.frombuffer(base64.b64decode(
            encoded_data.split(',')[1]), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # image = Image.open(
        #     BytesIO(base64.b64decode(encoded_data.split(',')[1])))
        # image.show()
        # cv2.imshow('img', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # frame = cv2.imread(frame)
        # liveimg = cv2.resize(img, (100, 100))
        # liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
        # input_vid.append(liveimg)
        # inp = np.array([input_vid[-24:]])
        # inp = inp/255
        # inp = inp.reshape(1, 24, 100, 100, 1)
        # pred = model.predict(inp)
        # print('Liveness: ' + pred[0][0])
        # input_vid = input_vid[-25:]

        if process_this_frame:  # pred[0][0]

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(
                small_frame, face_locations)
            # face_names = []
            for face_encoding in face_encodings:
                for ii in range(len(known_encods)):
                    # See if the face is a match for the known face(s)
                    match = face_recognition.compare_faces(
                        [known_encods[ii]], face_encoding)
                    if match[0]:
                        name = known_names[ii]
                        face_names.add(name)
                        print('face_names', face_names, sep=' ')
                        return jsonify(result=name)

        process_this_frame = not process_this_frame

        print('face_names', face_names, sep=' ')
        return jsonify(result='No face Detected')


if __name__ == '__main__':
    socketio.run(app)