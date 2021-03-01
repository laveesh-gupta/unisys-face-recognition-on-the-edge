from flask import Flask, render_template, request, abort, redirect
from flask_mysqldb import MySQL
from datetime import date
from werkzeug.utils import secure_filename
import yaml
import os
# import face_recognition
# import cv2
# import numpy as np
# from livenessmodel import get_liveness_model
# from common import get_users
# from flask_mail import *  
# from flask_mail import *
# from random import *
# from random import *  

# import pickle
# model = pickle.load(open('model.pkl', 'rb'))

app = Flask(__name__)

db = yaml.load(open("db.yaml"))
# mail = Mail(app)
# mail = Mail(app)
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

# app.config["MAIL_SERVER"]='smtp.gmail.com'  
# app.config["MAIL_PORT"] = 465      
# app.config["MAIL_USERNAME"] = 'lmn.rit22@gmail.com'  
# app.config['MAIL_PASSWORD'] = 'msrit2022'  
# app.config['MAIL_USE_TLS'] = False  
# app.config['MAIL_USE_SSL'] = True  
# mail = Mail(app)  
# otp = randint(000000,999999)   
app.config["MAIL_SERVER"] = "smtp.gmail.com" 
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'lmn.rit22@gmail.com' 
app.config["MAIL_PASSWORD"] = 'msrit2022'
app.config["MAIL_USE_TL"] = False
app.config["MAIL_USE_SSL"] = True
# mail = Mail (app)
# otp = randint(000000, 999999)

mysql = MySQL(app)

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
            print(detail[0][1])
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
    if request.method == "POST":
        f = request.files["file"]
        f.save(os.path.join("people", secure_filename(f.filename)))
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
            print(name, username, password)
            cur = mysql.connection.cursor()
            result = cur.execute("SELECT MAX(id) FROM employee")
            e_id = cur.fetchall()
            e_id = e_id[0][0]
            cur.execute(
                "INSERT INTO employee VALUES(" + str(e_id + 1) + ",%s,%s,%s)",
                (name, password, username),
            )
            mysql.connection.commit()
            return render_template("uploadfiles.html")
        
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


@app.route("/emp_login", methods=["GET", "POST"])
def login():
    # return "login"
    if request.method == "POST":
        userDetails = request.form
        username = userDetails["username"]
        # password = userDetails["password"]
        cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
        result = cur.execute("SELECT * FROM employee WHERE username = (%s) ",(username,))
        if result > 0:
            return redirect("/verify/"+username)
        return "<h1>Invalid Username</h1>"
    return render_template("login.html")


        # mysql.connection.commit()
        
    #         # print(result)
    #         today = date.today()
    #         # today = (today.strftime("%Y"))+"-"+(today.strftime("%m"))+"-"+(today.strftime("%d"))
    #         today = str(today)
    #         print(today)
    #         # stoday = today+""
    #         # print(typeof(today))
    #         # e_id = int(result.id)
    #         emp = cur.fetchall()
    #         # print(type(emp[0][0]))
    #         cur.execute(
    #             "insert into attd values(" + str(emp[0][0]) + ",'"+str(emp[0][3])+"','" + today + "',true);"
    #         )
    #         mysql.connection.commit()
    #         return render_template("success.html")
    #     else:
    #         cur.close()
    #         return render_template("fail.html")
    # return render_template("login.html")

# @app.rout('/verify',methods = ["POST"])

# @app.route('/verify/<username>',methods = ["POST","GET"])  
# def verify(username):  
#     if request.method == "GET" :
#         # email = request.form["email"] 
#         cur = mysql.connection.cursor()
#         result = cur.execute(
#             "SELECT email FROM employee WHERE username = (%s) ",
#             (username,)
#         )
#         emp = cur.fetchall()
#         email = emp[0][0]
#         otp = randint(000000, 999999)
#         # email = "nishitk@gmail.com"  
#         msg = Message('OTP',sender = 'lmn.rit22@gmail.com', recipients = [email])  
#         msg.body = str(otp)  
#         mail.send(msg)  
#         return render_template('verify.html')

#     else :
#         user_otp = request.form['otp'] 
#         print(otp) 
#         if otp == int(user_otp):

#             cur = mysql.connection.cursor()
#         # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
#             result = cur.execute(
#                 "SELECT * FROM employee WHERE username = (%s)",
#                 (username,)
#             )
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
#                     + today
#                     + "',true);"
#                 )
#                 mysql.connection.commit()
#                 return render_template("success.html")
#             except:
#                 return "<h1>Attendance already marked for the day.</h1>"

#             return render_template("success.html") 
#         return "<h3>failure, OTP does not match</h3>"

#     # email = request.form["email"]   
#     # msg = Message('OTP',sender = 'nishitk@gmail.com', recipients = [email])  
#     # msg.body = str(otp)  
#     # mail.send(msg)  
#     # return render_template('verify.html')  
 
# # @app.route('/validate',methods=["POST"])   
# # def validate():  
# #     user_otp = request.form['otp']  
# #     if otp == int(user_otp):  
# #         return render_template("success.html") 

# #     return "<h3>failure, OTP does not match</h3>"

# # @app.route("/flogin")
# # def flogin():

# #     font = cv2.FONT_HERSHEY_DUPLEX

# #     # Get the liveness network
# #     model = get_liveness_model()

# #     # load weights into new model
# #     model.load_weights("model/model.h5")
# #     print("Loaded model from disk")

# #     # Read the users data and create face encodings
# #     known_names, known_encods = get_users()

# #     video_capture = cv2.VideoCapture(0)
# #     video_capture.set(3, 640)
# #     video_capture.set(4, 480)

# #     # Initialize some variables
# #     face_locations = []
# #     face_encodings = []
# #     face_names = []
# #     process_this_frame = True
# #     input_vid = []
# #     recognized = []

# #     while True:
# #         # Grab a single frame of video
# #         if len(input_vid) < 24:

# #             ret, frame = video_capture.read()

# #             liveimg = cv2.resize(frame, (100, 100))
# #             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
# #             input_vid.append(liveimg)
# #         else:
# #             ret, frame = video_capture.read()

# #             liveimg = cv2.resize(frame, (100, 100))
# #             liveimg = cv2.cvtColor(liveimg, cv2.COLOR_BGR2GRAY)
# #             input_vid.append(liveimg)
# #             inp = np.array([input_vid[-24:]])
# #             inp = inp / 255
# #             inp = inp.reshape(1, 24, 100, 100, 1)
# #             pred = model.predict(inp)
# #             input_vid = input_vid[-25:]

# #             if pred[0][0] > 0.95:

# #                 # Resize frame of video to 1/4 size for faster face recognition processing
# #                 small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

# #                 # Only process every other frame of video to save time
# #                 if process_this_frame:
# #                     # Find all the faces and face encodings in the current frame of video
# #                     face_locations = face_recognition.face_locations(small_frame)
# #                     face_encodings = face_recognition.face_encodings(
# #                         small_frame, face_locations
# #                     )
# #                     name = "Unknown"
# #                     face_names = []
# #                     for face_encoding in face_encodings:
# #                         for ii in range(len(known_encods)):
# #                             # See if the face is a match for the known face(s)
# #                             match = face_recognition.compare_faces(
# #                                 [known_encods[ii]], face_encoding
# #                             )

# #                             if match[0]:
# #                                 name = known_names[ii]

# #                         face_names.append(name)

# #                 process_this_frame = not process_this_frame

# #                 unlock = False
# #                 for n in face_names:

# #                     if n != "Unknown":
# #                         unlock = True

# #                 # Display the results
# #                 for (top, right, bottom, left), name in zip(face_locations, face_names):
# #                     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
# #                     top *= 4
# #                     right *= 4
# #                     bottom *= 4
# #                     left *= 4

# #                     # Draw a box around the face
# #                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

# #                     # Draw a label with a name below the face
# #                     cv2.rectangle(
# #                         frame,
# #                         (left, bottom - 35),
# #                         (right, bottom),
# #                         (0, 0, 255),
# #                         cv2.FILLED,
# #                     )

# #                     cv2.putText(
# #                         frame,
# #                         name,
# #                         (left + 6, bottom - 6),
# #                         font,
# #                         1.0,
# #                         (255, 255, 255),
# #                         1,
# #                     )
# #                     if unlock:
# #                         cv2.putText(
# #                             frame,
# #                             "UNLOCK",
# #                             (frame.shape[1] // 2, frame.shape[0] // 2),
# #                             font,
# #                             1.0,
# #                             (255, 255, 255),
# #                             1,
# #                         )
# #                     else:
# #                         cv2.putText(
# #                             frame,
# #                             "LOCKED!",
# #                             (frame.shape[1] // 2, frame.shape[0] // 2),
# #                             font,
# #                             1.0,
# #                             (255, 255, 255),
# #                             1,
# #                         )
# #             else:
# #                 cv2.putText(
# #                     frame,
# #                     "WARNING!",
# #                     (frame.shape[1] // 2, frame.shape[0] // 2),
# #                     font,
# #                     1.0,
# #                     (255, 255, 255),
# #                     1,
# #                 )
# #             # Display the liveness score in top left corner
# #             cv2.putText(frame, str(pred[0][0]), (20, 20), font, 1.0, (255, 255, 0), 1)
# #             # Display the resulting image
# #             cv2.imshow("Video", frame)

# #             # Hit 'q' on the keyboard to quit!
# #             if cv2.waitKey(1) & 0xFF == ord("q"):
# #                 break

# #     # pickle.dump(model, open('model.pkl','wb'))
# #     # modelpkl = pickle.load(open('model.pkl','rb'))

# #     # Release handle to the webcam
# #     video_capture.release()
# #     cv2.destroyAllWindows()

# #     try:
# #         for x in face_names:
# #             if x not in recognized:
# #                 recognized.append(x)
    
# #     # userDetails = request.form
# #     # name = userDetails["name"]
# #     # username = userDetails["username"]
# #     # password = userDetails["password"]
# #         cur = mysql.connection.cursor()

# #         for x in recognized:
# #             print(x)
# #             result = cur.execute("SELECT id FROM employee where username='" + x + "';")
# #             e_id = cur.fetchall()
# #             e_id = e_id[0][0]
# #             today = date.today()
# #             today = str(today)
# #             cur.execute("INSERT INTO attd VALUES(" + str(e_id) + ",'"+x+"','" + today + "',true)")
# #             mysql.connection.commit()

# #         x=recognized[0]
# #         if x:
# #             return render_template("success.html")

# #         return render_template("flogin.html")
# #     except:
# #         return render_template("flogin.html")


if __name__ == "__main__":
    app.run(debug=True)