from flask import Flask, render_template, request, abort, redirect, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from werkzeug.utils import secure_filename
import yaml
import os
# import face_recognition
# import cv2
# import numpy as np
# from livenessmodel import get_liveness_model
# from common import get_users
from flask_mail import *
from random import *
from encryption import Encryptor
from flask_socketio import SocketIO, emit
import base64
import json
from engineio.payload import Payload
import time


# import pickle
# model = pickle.load(open('model.pkl', 'rb'))

app = Flask(__name__)

Payload.max_decode_packets = 200

db = yaml.load(open("db.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'lmn.rit22@gmail.com'
app.config["MAIL_PASSWORD"] = 'msrit2022'
app.config["MAIL_USE_TL"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)
otp = randint(100000, 999999)
key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
enc = Encryptor(key)

mysql = MySQL(app)

socketio = SocketIO(app, logger=True)


@socketio.on('connect')
def test_connect():
    print("SOCKET CONNECTED")


@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print("on_error: ", e, sep=' ')


@socketio.on_error('/login')  # handles the '/chat' namespace
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
count = 0

# face_names = []
input_vid = []


@app.route("/")
def index():
    # return "hey"
    return render_template("landing.html")


@app.route("/about")
def about():
    # return "about"
    return render_template("about.html")


@app.route("/ad_login", methods=["POST", "GET"])
def alogin():
    if request.method == "POST":
        userDetails = request.form
        username = userDetails["username"]
        password = userDetails["password"]
        cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
        result = cur.execute(
            "SELECT * FROM admin WHERE username = (%s) AND password = (%s)",
            (username, password),
        )
        # mysql.connection.commit()
        if result > 0:
            # print(result)
            return render_template("admin.html")
        else:
            cur.close()
            return render_template("fail.html")
    return render_template("adlogin.html")


@app.route("/emp/<id>")
def emp_detail(id):
    print(id)
    cur = mysql.connection.cursor()
    try:
        resultValue = cur.execute("SELECT * FROM attd where e_id=" + id + ";")
        if resultValue > 0:
            detail = cur.fetchall()
            print(detail)
            if detail:
                return render_template("emp_detail.html", detail=detail)
        else:
            return render_template("na.html")
    except:
        return render_template("na.html")


@app.route("/view_atd")
def view_atd():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM employee")
    if resultValue > 0:
        empDetails = cur.fetchall()
        return render_template("view_atd.html", empDetails=empDetails)
    # return render_template("view_atd.html")


@app.route("/uploadfile", methods=["GET", "POST"])
def uploadfile():
    enc.decrypt_all_files()
    if request.method == "POST":
        f = request.files["file"]
        f.save(os.path.join("people", secure_filename(f.filename)))
        enc.encrypt_all_files()
        return "<h1>Registration Successful</h1>"

    return render_template("uploadfile.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        if request.method == "POST":
            userDetails = request.form
            name = userDetails["name"]
            username = userDetails["username"]
            password = userDetails["password"]
            email = userDetails["email"]
            print(name, username, password)
            try:
                cur = mysql.connection.cursor()
                result = cur.execute("SELECT MAX(id) FROM employee")
                e_id = cur.fetchall()
                e_id = e_id[0][0]
                cur.execute(
                    "INSERT INTO employee VALUES(" +
                                                 str(e_id + 1) +
                                                     ",%s,%s,%s,%s)",
                    (name, password, username, email),
                )
                mysql.connection.commit()
                return render_template("uploadfiles.html")
            except:
                return "<h1>Already registered.</h1>"

        return render_template("register.html")
    except:
        return render_template("na.html")


# def upload_files():
#     uploaded_file = request.files['file']
#     filename = secure_filename(uploaded_file.filename)
#     if filename != '':
#         file_ext = os.path.splitext(filename)[1]
#         if file_ext not in app.config['UPLOAD_EXTENSIONS']:
#             abort(400)
#     uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
# return redirect(url_for('index'))


# @app.route("/emp_login", methods=["GET", "POST"])
# def login():
#     # return "login"
#     if request.method == "POST":
#         userDetails = request.form
#         username = userDetails["username"]
#         password = userDetails["password"]
#         cur = mysql.connection.cursor()
#         # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
#         result = cur.execute(
#             "SELECT * FROM employee WHERE username = (%s) AND password = (%s)",
#             (username, password),
#         )
#         # mysql.connection.commit()
#         if result > 0:
#             # print(result)
#             today = date.today()
#             # today = (today.strftime("%Y"))+"-"+(today.strftime("%m"))+"-"+(today.strftime("%d"))
#             today = str(today)
#             print(today)
#             # stoday = today+""
#             # print(typeof(today))
#             # e_id = int(result.id)
#             emp = cur.fetchall()
#             # print(type(emp[0][0]))
#             try:
#                 cur.execute(
#                     "insert into attd values("
#                     + str(emp[0][0])
#                     + ",'"
#                     + str(emp[0][3])
#                     + "','"
#                     + today
#                     + "',true);"
#                 )
#                 mysql.connection.commit()
#                 return render_template("success.html")
#             except:
#                 return "<h1>Attendance already marked for the day.</h1>"
#         else:
#             cur.close()
#             return render_template("fail.html")
#     return render_template("login.html")

@app.route("/emp_login", methods=["GET", "POST"])
def login():
    # return "login"
    if request.method == "POST":
        userDetails = request.form
        username = userDetails["username"]
        # password = userDetails["password"]
        cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
        result = cur.execute(
            "SELECT * FROM employee WHERE username = (%s) ", (username,))
        if result > 0:
            return redirect("/verify/"+username)
        return "<h1>Invalid Username</h1>"
    return render_template("login.html")


@app.route('/verify/<username>', methods=["POST", "GET"])
def verify(username):
    global otp
    if request.method == "GET":
        # email = request.form["email"]
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT email FROM employee WHERE username = (%s) ",
            (username,)
        )
        emp = cur.fetchall()
        email = emp[0][0]
        otp = randint(100000, 999999)
        # email = "nishitk@gmail.com"
        msg = Message('Authorization OTP',
                      sender='Administrator', recipients=[email])
        msg.body = "Hello "+username+"\nYour OTP is "+str(otp)
        mail.send(msg)
        return render_template('verify.html')

    else:
        user_otp = request.form['otp']
        print(otp)
        if otp == int(user_otp):

            cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
            result = cur.execute(
                "SELECT * FROM employee WHERE username = (%s)",
                (username,)
            )
            today = date.today()
            # today = (today.strftime("%Y"))+"-"+(today.strftime("%m"))+"-"+(today.strftime("%d"))
            today = str(today)
            print(today)
            # stoday = today+""
            # print(typeof(today))
            # e_id = int(result.id)
            emp = cur.fetchall()
            # print(type(emp[0][0]))

            try:
                cur.execute(
                    "insert into attd values("
                    + str(emp[0][0]) + ",'"
                    + str(emp[0][3])
                    + "','"
                    + today
                    + "',true);"
                )
                mysql.connection.commit()

                email = emp[0][4]
                msg = Message('Attendance Marked!!',
                              sender='Administrator', recipients=[email])
                msg.body = "We have marked your attendance! If it was not you contact the admin."
                mail.send(msg)

                return render_template("success.html")
            except:
                email = emp[0][4]
                msg = Message('Alert !', sender='Administrator',
                              recipients=[email])
                msg.body = "Multiple times attempt of marking your attendance! If it was not you contact the admin"
                mail.send(msg)
                return "<h1>Attendance already marked for the day.</h1>"

            # return render_template("success.html")

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                    "SELECT * FROM employee WHERE username = (%s)",
                    (username,)
                )

            emp = cur.fetchall()
            email = emp[0][4]
            msg = Message('Alert !! ', sender='Administrator',
                          recipients=[email])
            msg.body = "There was an attempt to mark your attendance with wrong credentials; if it was not you contact the admin."
            mail.send(msg)
            return "<h3>failure, OTP does not match</h3>"
        except:
            return "<h1>Error!!! </h1>"

# @app.route("/flogin")
# def flogin():

#     font = cv2.FONT_HERSHEY_DUPLEX

#     # Get the liveness network
#     model = get_liveness_model()

#     # load weights into new model
#     model.load_weights("model/model.h5")
#     print("Loaded model from disk")

#     # Read the users data and create face encodings
#     # known_names, known_encods = get_users()

#     video_capture = cv2.VideoCapture(0)
#     video_capture.set(3, 640)
#     video_capture.set(4, 480)

#     # Initialize some variables
#     face_locations = []
#     # face_encodings = []
#     # face_names = []
#     process_this_frame = True
#     input_vid = []

#     while True:
#         # Grab a single frame of video
#         if len(input_vid) < 24:

#             ret, frame = video_capture.read()

#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             input_vid.append(liveimg)
#         else:
#             ret, frame = video_capture.read()

#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             input_vid.append(liveimg)
#             inp = np.array([input_vid[-24:]])
#             inp = inp / 255
#             inp = inp.reshape(1, 24, 100, 100, 1)
#             pred = model.predict(inp)
#             input_vid = input_vid[-25:]

#             # if pred[0][0] > 0.95:

#             #     # Resize frame of video to 1/4 size for faster face recognition processing
#             #     small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#             #     # Only process every other frame of video to save time
#             #     if process_this_frame:
#             #         # Find all the faces and face locations in the current frame of video
#             #         face_locations = face_recognition.face_locations(small_frame)

#             #     process_this_frame = not process_this_frame

#             #     # unlock = False
#             #     # for n in face_names:

#             #     #     if n != "Unknown":
#             #     #         unlock = True

#             #     # Display the results
#             #     for (top, right, bottom, left) in face_locations:
#             #         # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#             #         top *= 4
#             #         right *= 4
#             #         bottom *= 4
#             #         left *= 4

#             #         # Draw a box around the face
#             #         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#             #         return redirect("/recognize")
#             # else:
#             #     cv2.putText(
#             #         frame,
#             #         "",
#             #         (frame.shape[1] // 2, frame.shape[0] // 2),
#             #         font,
#             #         1.0,
#             #         (255, 255, 255),
#             #         1,
#             #     )
#             # # Display the liveness score in top left corner
#             # cv2.putText(frame, str(pred[0][0]), (20, 20), font, 1.0, (255, 255, 0), 1)
#             # # Display the resulting image
#             # cv2.imshow("Video", frame)

#             # # Hit 'q' on the keyboard to quit!
#             # if cv2.waitKey(1) & 0xFF == ord("q"):
#             #     break

#     # pickle.dump(model, open('model.pkl','wb'))
#     # modelpkl = pickle.load(open('model.pkl','rb'))

#             if pred[0][0] > 0.95:
#                 break

#                 # Resize frame of video to 1/4 size for faster face recognition processing
#             #     small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#             #     # Only process every other frame of video to save time
#             #     if process_this_frame:
#             #         # Find all the faces and face locations in the current frame of video
#             #         face_locations = face_recognition.face_locations(small_frame)

#             #     process_this_frame = not process_this_frame

#             #     # unlock = False
#             #     # for n in face_names:

#             #     #     if n != "Unknown":
#             #     #         unlock = True

#             #     # Display the results
#             #     for (top, right, bottom, left) in face_locations:
#             #         # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#             #         top *= 4
#             #         right *= 4
#             #         bottom *= 4
#             #         left *= 4

#             #         # Draw a box around the face
#             #         cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#             #         return redirect("/recognize")
#             # else:
#             #     cv2.putText(
#             #         frame,
#             #         "",
#             #         (frame.shape[1] // 2, frame.shape[0] // 2),
#             #         font,
#             #         1.0,
#             #         (255, 255, 255),
#             #         1,
#             #     )
#             # # Display the liveness score in top left corner
#             # cv2.putText(frame, str(pred[0][0]), (20, 20), font, 1.0, (255, 255, 0), 1)
#             # Display the resulting image
#             cv2.imshow("Video", frame)

#             # Hit 'q' on the keyboard to quit!
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#     # Release handle to the webcam
#     video_capture.release()
#     cv2.destroyAllWindows()

#     if pred[0][0]>0.95:
#         return redirect("/recognize")

#     return render_template("flogin.html")

# @app.route("/recognize")
# def recognize():

#     font = cv2.FONT_HERSHEY_DUPLEX

#     # Get the liveness network
#     model = get_liveness_model()

#     # load weights into new model
#     model.load_weights("model/model.h5")
#     print("Loaded model from disk")

#     # Read the users data and create face encodings
#     known_names, known_encods = get_users()

#     video_capture = cv2.VideoCapture(0)
#     video_capture.set(3, 640)
#     video_capture.set(4, 480)

#     # Initialize some variables
#     face_locations = []
#     face_encodings = []
#     face_names = []
#     process_this_frame = True
#     input_vid = []
#     recognized = []

#     while True:
#         # Grab a single frame of video
#         if len(input_vid) < 24:

#             ret, frame = video_capture.read()

#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             input_vid.append(liveimg)
#         else:
#             ret, frame = video_capture.read()

#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             input_vid.append(liveimg)
#             inp = np.array([input_vid[-24:]])
#             inp = inp / 255
#             inp = inp.reshape(1, 24, 100, 100, 1)
#             pred = model.predict(inp)
#             input_vid = input_vid[-25:]

#             if pred[0][0] > 0.95:

#                 # Resize frame of video to 1/4 size for faster face recognition processing
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#                 # Only process every other frame of video to save time
#                 if process_this_frame:
#                     # Find all the faces and face encodings in the current frame of video
#                     face_locations = face_recognition.face_locations(small_frame)
#                     face_encodings = face_recognition.face_encodings(
#                         small_frame, face_locations
#                     )
#                     name = "Unknown"
#                     face_names = []
#                     for face_encoding in face_encodings:
#                         for ii in range(len(known_encods)):
#                             # See if the face is a match for the known face(s)
#                             match = face_recognition.compare_faces(
#                                 [known_encods[ii]], face_encoding
#                             )

#                             if match[0]:
#                                 name = known_names[ii]

#                         face_names.append(name)

#                 process_this_frame = not process_this_frame

#                 unlock = False
#                 for n in face_names:

#                     if n != "Unknown":
#                         unlock = True

#                 # Display the results
#                 for (top, right, bottom, left), name in zip(face_locations, face_names):
#                     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
#                     top *= 4
#                     right *= 4
#                     bottom *= 4
#                     left *= 4

#                     # Draw a box around the face
#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

#                     # Draw a label with a name below the face
#                     cv2.rectangle(
#                         frame,
#                         (left, bottom - 35),
#                         (right, bottom),
#                         (0, 0, 255),
#                         cv2.FILLED,
#                     )

#                     cv2.putText(
#                         frame,
#                         name,
#                         (left + 6, bottom - 6),
#                         font,
#                         1.0,
#                         (255, 255, 255),
#                         1,
#                     )
#                     if unlock:
#                         cv2.putText(
#                             frame,
#                             "UNLOCK",
#                             (frame.shape[1] // 2, frame.shape[0] // 2),
#                             font,
#                             1.0,
#                             (255, 255, 255),
#                             1,
#                         )
#                     else:
#                         cv2.putText(
#                             frame,
#                             "LOCKED!",
#                             (frame.shape[1] // 2, frame.shape[0] // 2),
#                             font,
#                             1.0,
#                             (255, 255, 255),
#                             1,
#                         )
#             else:
#                 cv2.putText(
#                     frame,
#                     "WARNING!",
#                     (frame.shape[1] // 2, frame.shape[0] // 2),
#                     font,
#                     1.0,
#                     (255, 255, 255),
#                     1,
#                 )
#             # Display the liveness score in top left corner
#             cv2.putText(frame, str(pred[0][0]), (20, 20), font, 1.0, (255, 255, 0), 1)
#             # Display the resulting image
#             cv2.imshow("Video", frame)

#             # Hit 'q' on the keyboard to quit!
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#     # pickle.dump(model, open('model.pkl','wb'))
#     # modelpkl = pickle.load(open('model.pkl','rb'))

#     # Release handle to the webcam
#     video_capture.release()
#     cv2.destroyAllWindows()

#     try:
#         for x in face_names:
#             if x not in recognized:
#                 recognized.append(x)

#     # userDetails = request.form
#     # name = userDetails["name"]
#     # username = userDetails["username"]
#     # password = userDetails["password"]
#         cur = mysql.connection.cursor()

#         for x in recognized:
#             print(x)
#             result = cur.execute("SELECT id FROM employee where username='" + x + "';")
#             e_id = cur.fetchall()
#             e_id = e_id[0][0]

# Changed from here for tin tout
#             today = datetime.now()
#             tdate = today.strftime("%d-%m-%Y")
#             ttime = today.strftime("%H:%M:%S")

#             result = cur.execute("SELECT* FROM attd where e_username='" + x + "' AND d='" + tdate +"';")

#              if result > 0 :
#                  tempp = cur.fetchall()
#                  temp1 = tempp[0]
#                  temp2 = tempp[-1]
#                  if temp1[4] === NULL or temp2[4] === NULL :
#                       cur.execute("UPDATE attd SET tout ='"+str(ttime)+"' WHERE e_id ="+str(e_id)+" AND tdate ='"+tdate+"' AND tout = NULL;")
#              else
#                  cur.execute(
#                  "insert into attd values("
#                   + str(e_id) + ",'"
#                   + x
#                   + "','"
#                   + str(tdate) + "','"+ str(ttime) + "', NULL);"
#                   )
#  Leave this line commented           cur.execute("INSERT INTO attd VALUES(" + str(e_id) + ",'"+x+"','" + today + "',true)")
#              mysql.connection.commit()

#         x=recognized[0]
#         if x:
#             return render_template("success.html")

#         return render_template("flogin.html")
#     except:
#         return render_template("flogin.html")


# @socketio.on('test liveness')
# def test_liveness(data):
#     global count
#     # time.sleep(1)
#     global input_vid, check_first, check_frame
#     if check_first is True:
#         check_frame = data['first_frame']
#         if check_frame is True:
#             check_first = False
#             input_vid = []
#             count = 0
#     # global i
#     # print(data['frameNo'])
#     # print(data)
#     # if(data['new_face'] == True):
#     #     input_vid = []
#     if check_frame is True:
#         if len(input_vid) < 24:
#             nparr = np.frombuffer(base64.b64decode(
#                 data['data'].split(',')[1]), np.uint8)
#             frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             # cv2.imwrite(str(i) + '.jpg', liveimg)
#             # i = i + 1
#             input_vid.append(liveimg)
#             print(len(input_vid))
#         else:
#             nparr = np.frombuffer(base64.b64decode(
#                 data['data'].split(',')[1]), np.uint8)
#             frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#             liveimg = cv2.resize(frame, (100, 100))
#             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#             # cv2.imwrite(str(i) + '.jpg', liveimg)
#             # i = i + 1
#             input_vid.append(liveimg)
#             inp = np.array([input_vid[-24:]])
#             inp = inp/255
#             inp = inp.reshape(1, 24, 100, 100, 1)
#             socketio.sleep(0)
#             pred = model.predict(inp)
#             input_vid = input_vid[-25:]
#             print(pred[0][0])
#             x = {'pred': str(pred[0][0])}
#             emit('liveness prediction', json.dumps(x))
#             if pred[0][0] <= .95:
#                 count = count + 1
#                 if count == 10:
#                     check_frame = False
#                     check_first = True
#                     z = {'stop': str(1)}
#                     emit('stop', json.dumps(z))
#                     return
#             else:
#                 # Resize frame of video to 1/4 size for faster face recognition processing
#                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
#                 # Find all the faces and face encodings in the current frame of video
#                 face_locations = face_recognition.face_locations(small_frame)
#                 face_encodings = face_recognition.face_encodings(
#                     small_frame, face_locations)
#                 # name = "Unknown"
#                 for face_encoding in face_encodings:
#                     for ii in range(len(known_encods)):
#                         # See if the face is a match for the known face(s)
#                         match = face_recognition.compare_faces(
#                             [known_encods[ii]], face_encoding)

#                         if match[0]:
#                             name = known_names[ii]
#                             face_names.add(name)
#                             break

#                 print('face_names', face_names, sep=' ')
#                 y = {'names': str(face_names)}
#                 emit('face names', json.dumps(y))
#                 check_first = True
#                 # input_vid = []
#                 cur = mysql.connection.cursor()

#                 try:
#                     # for x in face_names: #testing purpose
#                     #     # x = face_names[0]
#                     #     print(x)
#                     #     result = cur.execute(
#                     #         "SELECT id FROM employee where username='" + x + "';")
#                     #     e_id = cur.fetchall()
#                     #     e_id = e_id[0][0]
#                     #     # today = date.today()
#                     #     # today = str(today)
#                     #     # cur.execute("INSERT INTO attd VALUES(" +
#                     #     #             str(e_id) + ",'"+x+"','" + today + "',true)")
#                     #     # mysql.connection.commit()

#                     #     print("before before")

#                     #     today = datetime.now()
#                     #     tdate = today.strftime("%d-%m-%Y")
#                     #     ttime = today.strftime("%H:%M:%S")
                        
#                     #     print("before")
                        
#                     #     result = cur.execute("SELECT * FROM attd where e_username='" + str(x) + "' AND d='" + str(tdate) +"';")
                        
#                     #     print("after")
                        
#                     #     # tempp = cur.fetchall()
#                     #     # print(tempp)
#                     #     if result > 0 :
#                     #         print("inside if")
#                     #         tempp = cur.fetchall()
#                     #         temp1 = tempp[0]
#                     #         temp2 = tempp[-1]
#                     #         print(temp1, temp2)
#                     #         if temp1[4] == None or temp2[4] == None :
#                     #         # if temp1[4] == NULL:
#                     #             print("inside inside if")
#                     #             cur.execute("UPDATE attd SET t_out ='"+str(ttime)+"' WHERE e_id ="+str(e_id)+" AND d ='"+str(tdate)+"' AND t_out IS NULL;")
#                     #             mysql.connection.commit()
#                     #         else:
#                     #             print("inside inside else")
#                     #             cur.execute(
#                     #             "insert into attd values("
#                     #             + str(e_id) + ",'"
#                     #             + str(x)
#                     #             + "','"
#                     #             + str(tdate) + "','"+ str(ttime) + "', NULL);"
#                     #             )
#                     #             mysql.connection.commit()
                        
#                     #     else:
#                     #         print("inside else")
#                     #         cur.execute(
#                     #         "insert into attd values("
#                     #         + str(e_id) + ",'"
#                     #         + str(x)
#                     #         + "','"
#                     #         + str(tdate) + "','"+ str(ttime) + "', NULL);"
#                     #         )
#                     #         mysql.connection.commit()                     
#                     #     #  Leave this line commented           cur.execute("INSERT INTO attd VALUES(" + str(e_id) + ",'"+x+"','" + today + "',true)")
#                     #     result = cur.execute("SELECT * FROM employee where username='" + str(x) + "';")
#                     #     emp = cur.fetchall()
#                     #     email = emp[0][4]
#                     #     msg = Message('Attendance Marked!!',sender = 'Administrator', recipients = [email])  
#                     #     msg.body = "We have marked your attendance! If it was not you contact the admin."
#                     #     mail.send(msg)

#                     #     #delete name from recognized set
#                     #     face_names.remove(x)
#                     #     print("for loop completed")
         
#                     x = list(face_names)[0]
#                     print(x)
#                     result = cur.execute(
#                         "SELECT id FROM employee where username='" + x + "';")
#                     e_id = cur.fetchall()
#                     e_id = e_id[0][0]
#                         # today = date.today()
#                         # today = str(today)
#                         # cur.execute("INSERT INTO attd VALUES(" +
#                         #             str(e_id) + ",'"+x+"','" + today + "',true)")
#                         # mysql.connection.commit()

#                     print("before before")

#                     today = datetime.now()
#                     tdate = today.strftime("%d-%m-%Y")
#                     ttime = today.strftime("%H:%M:%S")
                        
#                     print("before")
                        
#                     result = cur.execute("SELECT * FROM attd where e_username='" + str(x) + "' AND d='" + str(tdate) +"';")
                        
#                     print("after")
                        
#                         # tempp = cur.fetchall()
#                         # print(tempp)
#                     if result > 0 :
#                         print("inside if")
#                         tempp = cur.fetchall()
#                         temp1 = tempp[0]
#                         temp2 = tempp[-1]
#                         print(temp1, temp2)
#                         if temp1[4] == None or temp2[4] == None :
#                         # if temp1[4] == NULL:
#                             print("inside inside if")
#                             cur.execute("UPDATE attd SET t_out ='"+str(ttime)+"' WHERE e_id ="+str(e_id)+" AND d ='"+str(tdate)+"' AND t_out IS NULL;")
#                             mysql.connection.commit()
#                         else:
#                             print("inside inside else")
#                             cur.execute(
#                             "insert into attd values("
#                             + str(e_id) + ",'"
#                             + str(x)
#                             + "','"
#                             + str(tdate) + "','"+ str(ttime) + "', NULL);"
#                             )
#                             mysql.connection.commit()
                        
#                     else:
#                         print("inside else")
#                         cur.execute(
#                         "insert into attd values("
#                         + str(e_id) + ",'"
#                         + str(x)
#                         + "','"
#                         + str(tdate) + "','"+ str(ttime) + "', NULL);"
#                         )
#                         mysql.connection.commit()                     
#                         #  Leave this line commented           cur.execute("INSERT INTO attd VALUES(" + str(e_id) + ",'"+x+"','" + today + "',true)")
#                     result = cur.execute("SELECT * FROM employee where username='" + str(x) + "';")
#                     emp = cur.fetchall()
#                     email = emp[0][4]
#                     msg = Message('Attendance Marked!!',sender = 'Administrator', recipients = [email])  
#                     msg.body = "We have marked your attendance! If it was not you contact the admin."
#                     mail.send(msg)

#                     #delete name from recognized set
#                     face_names.remove(x)
#                     print("for loop completed")
                        

#                 except:
#                     print("inside except")
#                     result = cur.execute("SELECT * FROM employee where username='" + x + "';")
#                     emp = cur.fetchall()
#                     print(result)
#                     print(emp)
#                     email = emp[0][4]
#                     msg = Message('Alert !',sender = 'Administrator', recipients = [email])  
#                     msg.body = "Multiple times attempt of marking your attendance."
#                     mail.send(msg) 
#                     # return "<h1>Attendance already marked for the day.</h1>"

#                 # if len(face_names):
#                 #     emit('redirect', {'url': 'success'})
                
#                 # if len(face_names):
#                 #     return render_template("success.html")

#                 # return render_template("loginnew.html")


# @app.route('/success')
# def new_view():
#     return render_template('success.html')


# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')

# @app.route('/login', methods=['GET', 'POST'])
# def flogin():
#     if request.method == 'GET':
#         # Read the users data and create face encodings
#         global known_names, known_encods
#         known_names, known_encods = get_users()
#         return render_template('loginnew.html'), 200
#     else:
#         global input_vid
#         process_this_frame = True

#         # input_vid = []
#         # frame = request.data
#         # print('frame: ', frame, sep=' ')
#         encoded_data = request.form['image']
#         # print('encoded_data: ', encoded_data[:20], sep=' ')
#         nparr = np.frombuffer(base64.b64decode(
#             encoded_data.split(',')[1]), np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         # image = Image.open(
#         #     BytesIO(base64.b64decode(encoded_data.split(',')[1])))
#         # image.show()
#         # cv2.imshow('img', img)
#         # cv2.waitKey(0)
#         # cv2.destroyAllWindows()
#         # frame = cv2.imread(frame)
#         # liveimg = cv2.resize(img, (100, 100))
#         # liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
#         # input_vid.append(liveimg)
#         # inp = np.array([input_vid[-24:]])
#         # inp = inp/255
#         # inp = inp.reshape(1, 24, 100, 100, 1)
#         # pred = model.predict(inp)
#         # print('Liveness: ' + pred[0][0])
#         # input_vid = input_vid[-25:]

#         if process_this_frame:  # pred[0][0]

#             # Resize frame of video to 1/4 size for faster face recognition processing
#             small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
#             face_locations = face_recognition.face_locations(small_frame)
#             face_encodings = face_recognition.face_encodings(
#                 small_frame, face_locations)
#             # face_names = []
#             for face_encoding in face_encodings:
#                 for ii in range(len(known_encods)):
#                     # See if the face is a match for the known face(s)
#                     match = face_recognition.compare_faces(
#                         [known_encods[ii]], face_encoding)
#                     if match[0]:
#                         name = known_names[ii]
#                         face_names.add(name)
#                         print('face_names', face_names, sep=' ')
#                         return jsonify(result=name)

#         process_this_frame = not process_this_frame

#         print('face_names', face_names, sep=' ')
#         return jsonify(result='No face Detected')


if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app)
