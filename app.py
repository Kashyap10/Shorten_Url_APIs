from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask,request,jsonify
from flask_restful import  Resource
from helper import Helper
from config import *
from tabledetails import Users
from flask_restful import Api
from urls import Urls

# Initiate flask app with and setup SQLAlchemy databse uri
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create db object  of SQLAlchemy
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class App_Users(db.Model):
    """
    Schema of users table
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    name = db.Column(db.String,nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    token = db.Column(db.String)

    def __init__(self, name,username,password,token):
        self.name = name
        self.username = username
        self.password = password
        self.token = token

    def __repr__(self):
        return f"<Name {self.name}>"

class Url_Details(db.Model):
    """
    Schema of urls table
    """
    __tablename__ = 'urls'
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    originalurl = db.Column(db.String)
    shortenurl = db.Column(db.String)

    def __init__(self, originalurl,shortenurl):
        self.originalurl = originalurl
        self.shortenurl = shortenurl

    def __repr__(self):
        return f"<Name {self.originalurl}>"

class SignUp(Resource):
    """
    Signup class for users
    """
    def post(self):
        '''
        This api takes body param like this
        {
            "username":"abc@xyz.com",
            "password":"abc123"
        }
        :return: It will return jwt token user need to pass this token in header like auth : eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDc4NjUxODYsImlhdCI6MTYwNzg2NTE4MSwidWlkIjoiYWJjQHh5ei5jb20iLCJyb2xlIjoxfQ.w8AmQHxeMD6lGk4_v21OJu1CVhZX6NdDpwqSb0317RE
        '''
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            userdata = App_Users.query.filter(App_Users.username == data['username']).first()
            if userdata:
                return jsonify({"msg": "Already Registered, please do login!!"})
            else:
                new_user = App_Users(name=data[Users.Name], username=data[Users.UserName],
                                     password=data[Users.Password],token=None)
                db.session.add(new_user)
                db.session.commit()
                return jsonify({"msg": "Successfully Registered"})


class Login(Resource):
    """
    Login class for users
    """
    def post(self):
        '''
        This api takes body param like this
        {
            "username":"abc@xyz.com",
            "password":"abc123"
        }
        :return: This api will check login based on given credentials
        '''
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            userdata = App_Users.query.filter(App_Users.username == data['username']).first()
            if userdata:
                pwddata = App_Users.query.filter(App_Users.password == data['password']).first()
                if pwddata:
                    token = Helper.encode_auth_token(data)
                    user_data = App_Users.query.filter(App_Users.username == data['username'],App_Users.password == data['password']).first()
                    userdata.token = token
                    db.session.add(user_data)
                    db.session.commit()
                    return jsonify({"msg": "Login Successful!!","token": str(token)})
                else:
                    return jsonify({"msg": "Invalid Password. Please enter correct password"})
            else:
                return jsonify({"msg": "Invalid Username.Please enter correct username or Please do registration first."})

class Shorten_Url(Resource):
    def post(self):
        '''
            This method will take original url as body parameter and will return short url
        '''

        tokenresponse = Helper.decode_auth_token(request.headers.get('auth'))

        if tokenresponse and tokenresponse in ['Signature expired. Please log in again.']:
            return jsonify({"response":'Signature expired. Please log in again.'})
        elif tokenresponse and tokenresponse in ['Invalid token. Please log in again.']:
            return jsonify({"response":"Invalid token. You are not authorized to access this resource."})
        elif tokenresponse:
            data = request.get_json()
            if not data:
                data = {"response": "No data available in payload"}
                return jsonify(data)
            else:
                url = data['url']
                url_data =  Url_Details.query.filter(Url_Details.originalurl == url).first()
                if url_data:
                    shorturl = url_data.shortenurl
                else:
                    shorturl  = Helper.get_shorten_url(url)
                    new_url = Url_Details(originalurl=url, shortenurl=shorturl)
                    db.session.add(new_url)
                    db.session.commit()
                return jsonify({"shorturl":str(shorturl)})

class Original_Url(Resource):
    def post(self):
        '''
        This method will take Short url as body parameter and will return original url
        '''

        tokenresponse = Helper.decode_auth_token(request.headers.get('auth'))

        if tokenresponse and tokenresponse in ['Signature expired. Please log in again.']:
            return jsonify({"response": 'Signature expired. Please log in again.'})
        elif tokenresponse and tokenresponse in ['Invalid token. Please log in again.']:
            return jsonify({"response": "Invalid token. You are not authorized to access this resource."})
        elif tokenresponse:
            data = request.get_json()
            if not data:
                data = {"response": "No data available in payload"}
                return jsonify(data)
            else:
                url_data = Url_Details.query.filter(Url_Details.shortenurl == data['url']).first()
                if url_data:
                    orginalurl = url_data.originalurl
                    return jsonify({"orginalurl": str(orginalurl)})
                else:
                    return jsonify({"msg": "Original url does not exists. You need to shorten this url first."})

api = Api(app)
api.add_resource(SignUp, Urls.Signup)
api.add_resource(Login, Urls.Login)
api.add_resource(Original_Url, Urls.OriginalUrl)
api.add_resource(Shorten_Url, Urls.ShortenUrl)

if __name__ == '__main__':
    app.run()