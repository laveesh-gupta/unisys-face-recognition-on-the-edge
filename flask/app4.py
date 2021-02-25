from flask import Flask, render_template, request, jsonify
import face_recognition
import face_recognition
import cv2
import numpy as np
from flask_socketio import SocketIO, emit
from livenessmodel import get_liveness_model
from common import get_users
import base64


app = Flask(__name__)
socketio = SocketIO(app)


@socketio.on('connect')
def test_connect():
    print("SOCKET CONNECTED")


# Get the liveness network
model = get_liveness_model()

# load weights into new model
model.load_weights("model/model.h5")
print("Loaded model from disk")

# Read the users data and create face encodings
known_names, known_encods = get_users()
face_names = set()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
input_vid = []


@app.route('/')
def hello():
    return 'Hello, World!'


@socketio.on('test liveness')
def test_liveness(data):
    global input_vid
    # print(data)
    if len(input_vid) < 24:
        nparr = np.fromstring(base64.b64decode(
            data['data'].split(',')[1]), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        liveimg = cv2.resize(frame, (100, 100))
        liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
        input_vid.append(liveimg)
        print(len(input_vid))
    else:
        nparr = np.fromstring(base64.b64decode(
            data['data'].split(',')[1]), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        liveimg = cv2.resize(frame, (100, 100))
        liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
        input_vid.append(liveimg)
        inp = np.array([input_vid[-24:]])
        inp = inp/255
        inp = inp.reshape(1, 24, 100, 100, 1)
        pred = model.predict(inp)
        input_vid = input_vid[-25:]
        print(pred[0][0])
        emit('liveness prediction', jsonify(pred=pred[0][0]))


@app.route('/login2', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login2.html'), 200
    else:
        # Initialize some variables
        face_locations = []
        face_encodings = []

        # input_vid = []
        # frame = request.data
        # print('frame: ', frame, sep=' ')
        encoded_data = request.form['image']
        # print('encoded_data: ', encoded_data[:20], sep=' ')
        nparr = np.fromstring(base64.b64decode(
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

        if 1 > .95:  # pred[0][0]

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
                        return jsonify(result=name)
        print('face_names', face_names, sep=' ')
        return jsonify(result='No face Detected')


if __name__ == '__main__':
    socketio.run(app)
