from flask import render_template,redirect,request, session, flash, url_for
from flask_app import app
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
bcrypt = Bcrypt(app)
UPLOAD_FOLDER = 'flask_app/static/img/profile_pics'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/") #Display Landing Page
def index():
    return render_template("index.html")

@app.route("/signin") #Display the Login and Registration Page
def signin():
    return render_template("login.html")

@app.route("/register", methods=["Post"]) #Register an Account
def register():
    if not User.validate_new_user(request.form):
        return redirect('/signin')
    data = {
        "name": request.form['name'],
        "email": request.form['email'],
        "password": bcrypt.generate_password_hash(request.form['password']),
    }
    session['id'] = User.new_user(data)
    return redirect("/setup")

@app.route("/setup") #New Registration Set up
def setup():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    return render_template("setup.html", user = User.get_user_by_id(data))

@app.route("/register_player", methods=["Post"]) #submit player information
def register_player():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": request.form['user_id'],
        "experience": request.form['experience'],
        "class1": request.form['class1'],
        "class2": request.form['class2'],
        "class3": request.form['class3'],
        "availability": request.form['availability'],
        "bio": request.form['bio']
    }
    if not User.validate_player_info(data):
        return redirect('/setup')
    User.register_player(data)
    return redirect("/dashboard")

@app.route("/register_dm", methods=["Post"]) #submit player information
def register_dm():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": request.form['user_id'],
        "experience": request.form['experience'],
        "availability": request.form['availability'],
        "bio": request.form['bio']
    }
    if not User.validate_dm_info(data):
        return redirect('/setup')
    User.register_dm(data)
    return redirect("/dashboard")

@app.route("/login", methods=["Post"]) #Log into Account
def login():
    user = User.get_user_by_email(request.form)
    if not user:
        flash("The email and password combination is incorrect.", "registration")
        return redirect('/signin')
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("The email and password combination is incorrect.", "registration")
        return redirect('/signin')
    session['id'] = user.id
    return redirect("/dashboard")

@app.route("/logout") #Logout
def logout():
    session.clear()
    return redirect("/")

@app.route("/profile") #User Profile
def profile():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    return render_template("profile.html", user = User.get_user_by_id(data), player_info = User.get_player_info_by_id(data), dm_info = User.get_dm_info_by_id(data))

@app.route("/profile/edit") #Edit User Profile
def edit_profile():
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": session['id']
    }
    return render_template("edit_profile.html", user = User.get_user_by_id(data), player_info = User.get_player_info_by_id(data), dm_info = User.get_dm_info_by_id(data))

@app.route("/profile/<int:id>") #View User's Profile
def view_profile(id):
    if 'id' not in session:
        return redirect("/logout")
    data = {
        "user_id": id
    }
    return render_template("profile.html", user = User.get_user_by_id(data), player_info = User.get_player_info_by_id(data), dm_info = User.get_dm_info_by_id(data))

@app.route("/update_player_info", methods=["Post"]) #Update Player Info
def update_player_info():
    if 'id' not in session:
        return redirect("/profile")
    data = {
        "user_id": request.form['user_id'],
        "experience": request.form['experience'],
        "class1": request.form['class1'],
        "class2": request.form['class2'],
        "class3": request.form['class3'],
        "availability": request.form['availability'],
        "bio": request.form['bio']
    }
    User.update_player_info(data)
    return redirect("/profile")

@app.route("/update_dm_info", methods=["Post"]) #Update DM Info
def update_dm_info():
    if 'id' not in session:
        return redirect("/profile")
    data = {
        "user_id": request.form['user_id'],
        "experience": request.form['experience'],
        "availability": request.form['availability'],
        "bio": request.form['bio']
    }
    User.update_dm_info(data)
    return redirect("/profile")

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            root = secure_filename(file.filename)
            filename = f"{session['id']}{root}"
            data = {
                "user_id": session['id'],
                "profile_pic": filename
            }
            User.update_profile_pic(data)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('download_file', name=filename))
    return redirect("/profile")
