from flask import Flask , render_template

app = Flask(__name__)

@app.route('/')
def index():
    # return "hey"
    return render_template('landing.html')

@app.route('/about')
def about():
    # return "about"
    return render_template('about.html')


@app.route('/login')
def login():
    # return "login"
    return render_template('login.html')


@app.route('/flogin')
def flogin():
    return render_template('flogin.html')
if __name__ == "__main__" :
    app.run(debug=True)

        