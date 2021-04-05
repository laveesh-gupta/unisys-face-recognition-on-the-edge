from flask import Flask, render_template, request, abort, redirect, jsonify
from flask_mysqldb import MySQL
# from datetime import 
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
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity,set_access_cookies,unset_jwt_cookies, create_refresh_token
)
from flask.helpers import make_response, url_for
# import pickle
# model = pickle.load(open('model.pkl', 'rb'))

app = Flask(__name__)

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
mail = Mail (app)
otp = randint(100000, 999999)
key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
enc = Encryptor(key)

mysql = MySQL(app)

app.config['JWT_SECRET_KEY'] = 'secret-secret'  # Change this!
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
jwt = JWTManager(app)

@app.route("/", methods=["POST", "GET"])
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
            access_token = create_access_token(identity={"username": username})
            refresh_token = create_refresh_token(identity ={'username': username})
            # response = jsonify({'login': True})
            resp = make_response(redirect(url_for('home')))
            set_access_cookies(resp,access_token)

            return resp
            # return render_template("admin.html")
        else:
            cur.close()
            return render_template("fail.html")
    return render_template("adlogin.html")

@app.route("/home")
@jwt_required()
def home() :
    return render_template("admin.html")

@app.route("/emp/<id>")
@jwt_required()
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
@jwt_required()
def view_atd():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM employee")
    if resultValue > 0:
        empDetails = cur.fetchall()
        return render_template("view_atd.html", empDetails=empDetails)
    return render_template("na.html")


@app.route("/uploadfile", methods=["GET", "POST"])
# @jwt_required()
def uploadfile():
    enc.decrypt_all_files()
    if request.method == "POST":
        f = request.files["file"]
        f.save(os.path.join("people", secure_filename(f.filename)))
        enc.encrypt_all_files()
        return render_template("regsuc.html")

    return render_template("uploadfile.html")


@app.route("/register", methods=["GET", "POST"])
# @jwt_required()
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
                    "INSERT INTO employee VALUES(" + str(e_id + 1) + ",%s,%s,%s,%s)",
                    (name, password, username,email),
                )
                mysql.connection.commit()
                return render_template("uploadfiles.html")
            except:
                return render_template("alrreg.html")

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
# @jwt_required()
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
        return render_template("na.html")
    return render_template("login.html")

@app.route('/verify/<username>',methods = ["POST","GET"])  
# @jwt_required()
def verify(username):
    global otp
    if request.method == "GET" :
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
        msg = Message('Authorization OTP',sender = 'Administrator', recipients = [email])  
        msg.body = "Hello "+username+"\nYour OTP is "+str(otp)
        mail.send(msg)  
        return render_template('verify.html')

    else :
        user_otp = request.form['otp'] 
        print(otp) 
        if otp == int(user_otp):

            cur = mysql.connection.cursor()
        # cur.execute("INSERT INTO users(name, password) VALUES(%s, %s)",(name, password))
            result = cur.execute(
                "SELECT * FROM employee WHERE username = (%s)",
                (username,)
            )
            # today = date.today()
            # today = (today.strftime("%Y"))+"-"+(today.strftime("%m"))+"-"+(today.strftime("%d"))
            # today = str(today)
            # todayDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            today = datetime.now()

            tdate = today.strftime("%d-%m-%Y")
            ttime = today.strftime("%H:%M:%S")
            print(today, tdate, ttime)

            # stoday = today+""
            # print(typeof(today))
            # e_id = int(result.id)
            
            emp = cur.fetchall()
            
            # print(type(emp[0][0]))
            
            print(emp)
            try:
                cur.execute(
                    "insert into attd values("
                    + str(emp[0][0]) + ",'"
                    + str(emp[0][3])
                    + "','"
                    + str(tdate) + "','"+ str(ttime) + "','"
                    + str(ttime) +"');"
                )
                mysql.connection.commit()
  
                email = emp[0][4]
                msg = Message('Attendance Marked!!',sender = 'Administrator', recipients = [email])  
                msg.body = "We have marked your attendance! If it was not you contact the admin."
                mail.send(msg)  

                return render_template("success.html")
            except:
                email = emp[0][4]
                msg = Message('Alert !',sender = 'Administrator', recipients = [email])  
                msg.body = "Multiple times attempt of marking your attendance! If it was not you contact the admin"
                mail.send(msg) 
                return render_template("alratd.html")

            # return render_template("success.html")
        
        try: 
            cur = mysql.connection.cursor()
            cur.execute(
                    "SELECT * FROM employee WHERE username = (%s)",
                    (username,)
                )
        
            emp = cur.fetchall()
            email = emp[0][4]
            msg = Message('Alert !! ',sender = 'Administrator', recipients = [email])  
            msg.body = "There was an attempt to mark your attendance with wrong credentials; if it was not you contact the admin."
            mail.send(msg)  
            return render_template("fail.html")
        except :
            return "<h1>Error!!! </h1>"

if __name__ == "__main__":
    app.run(debug=True)