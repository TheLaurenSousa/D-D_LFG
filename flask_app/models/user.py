from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
email_regex = re.compile(r'^[a-zA-z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$')
db = "danddlfg"

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.password = data['password']
        self.profile_pic = data['profile_pic']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    @classmethod
    def new_user(cls, data):
        query = "INSERT INTO users (name, email, password, profile_pic) VALUES (%(name)s, %(email)s, %(password)s, 'default.png');"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def get_user_by_email(cls, data):
        query = "SELECT * FROM users WHERE email= %(email)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0])

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id= %(user_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        return cls(results[0])
    
    @classmethod
    def get_player_info_by_id(cls, data):
        query = "SELECT * FROM player_info WHERE user_id = %(user_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) == 0:
            return False
        return results[0]

    @classmethod
    def get_dm_info_by_id(cls, data):
        query = "SELECT * FROM dm_info WHERE user_id = %(user_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) == 0:
            return False
        return results[0]

    @classmethod
    def get_dm_status_by_id(cls, data):
        query = "SELECT * FROM dm_info WHERE user_id = %(user_id)s;"
        results = connectToMySQL(db).query_db(query, data)
        if len(results) != 0:
            return True
        return False

    @classmethod
    def register_player(cls, data):
        query = "INSERT INTO player_info (user_id, experience, class1, class2, class3, availability, bio) VALUES (%(user_id)s, %(experience)s, %(class1)s, %(class2)s, %(class3)s, %(availability)s, %(bio)s);"
        return connectToMySQL(db).query_db(query, data)
    
    @classmethod
    def register_dm(cls, data):
        query = "INSERT INTO dm_info (user_id, experience, availability, bio) VALUES (%(user_id)s, %(experience)s, %(availability)s, %(bio)s);"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def update_player_info(cls, data):
        query = "UPDATE player_info SET experience = %(experience)s, class1 = %(class1)s, class2 = %(class2)s, class3 = %(class3)s, availability = %(availability)s, bio = %(bio)s WHERE user_id = %(user_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def update_dm_info(cls, data):
        query = "UPDATE dm_info SET experience = %(experience)s, availability = %(availability)s, bio = %(bio)s WHERE user_id = %(user_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @classmethod
    def update_profile_pic(cls, data):
        query = "UPDATE users SET profile_pic = %(profile_pic)s WHERE id = %(user_id)s;"
        return connectToMySQL(db).query_db(query, data)

    @staticmethod
    def validate_new_user(data):
        is_valid = True
        if len(data['name']) == 0 or len(data['email']) == 0 or len(data['password']) == 0 or len(data['confirm_password']) == 0:
            is_valid = False
            flash("All fields are required.", "registration")
        if len(data['name']) < 2:
            is_valid = False
            flash("First Name must be at least 2 characters", "registration")
        if not email_regex.match(data['email']) or len(data['email']) < 3:
            flash("Invalid email address.", "registration")
            is_valid = False
        if email_regex.match(data['email']):
            query = "SELECT * FROM users WHERE email=%(email)s"
            results = connectToMySQL(db).query_db(query, data)
            if results:
                flash("The email is already registered.", "registration")
                is_valid = False
        if not password_regex.match(data['password']):
            is_valid = False
            flash("Password must be at least 8 characters and include at least one number and one uppercase letter", "registration")
        if data['password'] != data['confirm_password']:
            is_valid = False
            flash("Make sure your password is entered correctly into both fields", "registration")
        return is_valid

    @staticmethod
    def validate_player_info(data):
        is_valid = True
        checker = User.get_player_info_by_id(data)
        if checker != False:
            is_valid = False
            flash("It looks like you have already submitted Player information. Try updating your profile instead.", "registration")
        if len(data['experience']) == 0 or len(data['class1']) == 0 or len(data['class2']) == 0 or len(data['class3']) == 0 or len(data['availability']) == 0 or len(data['bio']) == 0:
            is_valid = False
            flash("All fields are required.", "registration")
        return is_valid

    @staticmethod
    def validate_dm_info(data):
        is_valid = True
        checker = User.get_dm_info_by_id(data)
        if checker != False:
            is_valid = False
            flash("It looks like you have already submitted DM information. Try updating your profile instead.", "registration")
        if len(data['experience']) == 0 or len(data['availability']) == 0 or len(data['bio']) == 0:
            is_valid = False
            flash("All fields are required.", "registration")
        return is_valid