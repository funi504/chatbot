from http import client
import os
import flask
from flask import *
from flask_cors import CORS ,cross_origin
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from databaseModel import  db , User , Project,Workflow, EmailConfig, googleApiConfig
from config import ApplicationConfig , configEmail
from create_mail import create_message , send_email
import json ,datetime 
from urllib.parse import urlparse
from llm import message_reply
from routes.profile import get_current_user
from routes.project import create_project
from routes.workflow import workflow
from routes.uploading_url import upload_url_webscrapping
from routes.register import register_user
from routes.confirm_email import confirm_user_email
from routes.change_password import  change_user_password
from routes.forgot_password import forgot_user_password
from routes.login import login_user
from routes.logout import logout_user
from routes.AIreply import AI_reply_to_user
from routes.initial_nodes import initial_reply_Nodes
from routes.reply import reply_user
from routes.email import send_email_to_user
from routes.email_config import emailConfiguration

app = Flask(__name__)
CORS(app, supports_credentials=True,)
app.config['CORS_HEADERS'] = 'application/json'
app.config.from_object(ApplicationConfig)
bcrypt = Bcrypt(app)
server_session = Session(app)
mail = Mail(app)

CLIENT_SECRETS_FILE = "credentials.json"

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app.secret_key = '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'
s = URLSafeTimedSerializer('Thisisasecret!-fjvnnjj2@123vvjk45ancnv9*')

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/@me' ,methods = ['GET', 'PUT', 'DELETE'])
def get_user():
    resp = get_current_user(session , User , request , jsonify , db , bcrypt )
    return resp


@app.route("/project" , methods=["POST","GET","DELETE", "PUT"])
def project():
    resp = create_project(session , Project , request , jsonify , db)
    return resp

@app.route("/workflow", methods=["POST","GET","DELETE"])
def work_flow():
    resp = workflow(session , Project , request , Workflow , jsonify ,db )
    return resp


@app.route('/upload_url_webscrapping' , methods=["POST","GET","PUT"])
def upload_url():
    resp = upload_url_webscrapping(session , Project , jsonify , request)
    return resp


@app.route('/register' ,methods = ['POST'])
def register_new_user():
    resp = register_user( configEmail , app ,request ,bcrypt ,User, jsonify ,db , s , Message ,url_for ,mail , datetime)
    return resp

@app.route('/confirm_email/<token>')
def confirm_my_email(token):
    resp = confirm_user_email(token , s ,User ,db , datetime , SignatureExpired)
    return resp


@app.route('/change_password/<token>', methods=['POST', 'GET'])
def change_my_password(token):
    resp = change_user_password(token ,request , s , User , bcrypt ,db ,render_template)
    return resp

@app.route('/forgot_password',methods=["POST"])
def forgot_my_password():
    resp = forgot_user_password(configEmail , app , request , s ,Message , url_for , mail , jsonify)
    return resp


@app.route('/login' ,methods = ['POST'])
def log_user_in():
    resp = login_user(configEmail,app,request,User,bcrypt,jsonify,Message,s,url_for,mail,session,flask)
    return resp


@app.route("/logout", methods=["POST"])
def log_user_out():
    resp = logout_user(session)
    return resp

@app.route('/AIreply', methods = ['POST'])
def AI_reply():
    resp = AI_reply_to_user(request , message_reply)
    return resp

@app.route('/initialNodes', methods = ['POST'])
def initialNodes():
    resp = initial_reply_Nodes(request,Project,Workflow,jsonify)
    return resp

@app.route('/reply', methods = ['POST'])
def create_reply():
    resp = reply_user(request,Project,Workflow,jsonify)
    return resp


@app.route('/email', methods = ['POST'])
def send_email():
    resp = send_email_to_user(request, EmailConfig , app , Mail , Message ,jsonify)
    return resp
        

@app.route('/emailConfig', methods=['POST','GET','PUT','DELETE'])
def emailConfig():
    resp = emailConfiguration(request, session, EmailConfig ,jsonify , Project , db )
    return resp


# main driver function
if __name__ == '__main__':
 
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080)