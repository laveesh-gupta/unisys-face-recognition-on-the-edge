from flask import Flask, render_template, request
import face_recognition
# import face_recognition
import cv2
import numpy as np
# from livenessmodel import get_liveness_model
from common import get_users
import base64


app = Flask(__name__)

# # Get the liveness network
# model = get_liveness_model()

# # load weights into new model
# model.load_weights("model/model.h5")
# print("Loaded model from disk")

# Read the users data and create face encodings
known_names, known_encods = get_users()
face_names = set()


@app.route('/')
def hello():
    return 'Hello, World!'


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
                        break
        print('face_names', face_names, sep=' ')
        return 'Success'

if __name__ == "__main__":
    app.run(debug=True)
