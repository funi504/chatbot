import os
from flask import *
from flask_cors import CORS ,cross_origin
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from chat import chatFunc
from train import train
from  databaseModel import  db , User , Project
from config import ApplicationConfig
import json ,datetime 
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app, supports_credentials=True,)
app.config['CORS_HEADERS'] = 'application/json'
app.config.from_object(ApplicationConfig)
bcrypt = Bcrypt(app)
server_session = Session(app)
mail = Mail(app)

s = URLSafeTimedSerializer('Thisisasecret!-fjvnnjj2@123vvjk45ancnv9*')

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/@me' ,methods = ['GET', 'PUT', 'DELETE'])

def get_current_user():
    try:
        user_id = session.get("user_id")
        print(user_id)
    except:
        return jsonify({ "error": "account not found"}),401

    if request.method =="GET":
        try:
            user = User.query.filter_by(id=user_id).first()

            return jsonify({
            "id": user.id,
            "email": user.email,
            "domain" : user.domain
        })
        except:
            return jsonify({ "error": "account not found"}),401


    if request.method == "PUT":
        try:

            user = User.query.filter_by(id=user_id).first()

            email = request.json["email"]
            domain = request.json["domain"]

            user.email = email
            user.domain = domain

            db.session.commit()

            return jsonify({
                "new_email": user.email,
                "new_domain": user.domain
            })
        except:
            return jsonify({ "error": "account not found"}),401

    if request.method == "DELETE":
        try:
            user = User.query.filter_by(id=user_id).first()
            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "the account has been deleted"})
        except:
            return jsonify({"error":"account not found"})

@app.route("/project" , methods=["POST","GET","DELETE", "PUT"])
def create_Project():
    user_id =session.get("user_id")

    if request.method == "POST":
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            project_name = request.json["Name"]

            new_project = Project(user_id=user_id ,project_name=project_name)
            db.session.add(new_project)
            db.session.commit()

            return jsonify({
                "Name": new_project.project_name,
                "project_Id": new_project.project_id,
                "user_Id": new_project.user_id

            })
        except:
            return jsonify({ "error": "something went wrong , try later"})
    
    if request.method == "GET":
        project = Project.query.filter_by(user_id=user_id).first()

        if not user_id:
            return jsonify({"error":"no project found"}),401

        if not project:
            return jsonify({"error":"unauthorized, no project id found"}),401

        return jsonify({

            "projectName": project.project_name,
            "projectId": project.project_id,
            "userId": project.user_id,
        })

    if request.method == "DELETE":
        try:
            project = Project.query.filter_by(user_id=user_id).first()
            project_id = project.project_id

            if not user_id:
                return jsonify({"error":"unauthorized"}),401

            if not project_id:
                return jsonify({"error":"unauthorized"}),401
            
            #delete project , intent file and bot model
            intent_path = project_id +"json"
            bot_path = project_id + ".pth"

            if os.path.exists(intent_path):
                os.remove(intent_path)

            if os.path.exists(bot_path):
                os.remove(bot_path)

            
            project = Project.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            return jsonify({"message": "the project has been deleted"})
        
        except:
            return jsonify({ "error": "something went wrong , try later"})
        

    if request.method == "PUT":
        try:
            project = Project.query.filter_by(user_id=user_id).first()

            if not user_id:
                return jsonify({"error":"unauthorized"}),401

            if not project:
                return jsonify({"error":"unauthorized"}),401
            
            name = request.json["Name"]
            project.project_name = name
            db.session.commit()

            return jsonify({
                "Name": project.project_name,
                "project_Id": project.project_id,
                "user_Id": project.user_id

            })

        except Exception as error:
            print(error)
            return jsonify({ "error": "something went wrong , try later"})


@app.route('/intent' , methods=["POST","GET","PUT"])
def intent():

    user_id = session.get("user_id")
    project = Project.query.filter_by(user_id=user_id).first()
    project_id = project.project_id
    filename = project_id+".json"
    print(filename)

    if not user_id:
        return jsonify({"error":"unauthorized"}),401

    if not project_id:
        return jsonify({"error":"project does not exist"}),401
    
    if request.method == "POST":

        #create an intent file
        intent_data= request.json
        
        #add contents to the file
        save_file = open(filename,"w")
        json.dump(intent_data ,save_file, indent=6)
        save_file.close()

        f = open(filename)
        data = json.load(f)
        f.close()
        return jsonify(data)

    if request.method == "GET":

        f = open(filename)
        data = json.load(f)
        f.close()
        return jsonify(data)

    if request.method == "PUT":

        #create an intent file
        intent_data= request.json
        
        #add contents to the file
        save_file = open(filename,"w")
        json.dump(intent_data ,save_file, indent=6)
        save_file.close()

        f = open(filename)
        data = json.load(f)
        f.close()
        return jsonify(data)

    
@app.route('/trainmodel')
def train_model():
    user_id = session.get("user_id")
    project = Project.query.filter_by(user_id=user_id).first()
    project_id = project.project_id

    if not user_id:
        return jsonify({"error":"unauthorized"}),401

    if not project_id:
        return jsonify({"error":"project does not exist"}),401
    
    train(project_id)

    return jsonify({"message":"model trained"})

#TODO : check if email confirmation is working
@app.route('/register' ,methods = ['POST'])
def register_user():
    try:
        email =  request.json["email"]
        domain = request.json["domain"]
        password = request.json["password"]
        hashedPassword = bcrypt.generate_password_hash(password)
        date =  datetime.date.today()

        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            return jsonify({"error": "email already exists"}), 409

        new_user = User(email=email , domain=domain , password=hashedPassword,
                        created_on=date, 
                        )
        db.session.add(new_user)
        db.session.commit()

        #session["user_id"] = new_user.id

        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Confirm Email', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({
            "id": new_user.id,
            "email": new_user.email,
            "domain" : new_user.domain,
            "message":"email confirmation sent , confirm email before 1 hours"
        })

    except :
        return jsonify({"error": "the was an error registering your account"})


#TODO : check if email confirmation is working when you create an account
@app.route('/confirm_email/<token>')
def confirm_email(token):

    try:
        email = s.loads(token, salt='email-confirm-salt-wufksk12@58', max_age=3600)
        user = User.query.filter_by(email=email).first()
        user.confirmed = True
        user.confirmed_on = datetime.date.today()
        db.session.commit()

    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return '<h1>email has been verified!, you can now log in</h1>'


@app.route('/change_password/<token>', methods=['POST'])
def change_password(token):

    try:
        email = s.loads(token, salt='email-confirm-salt-wufksk12@58', max_age=3600)
        new_password = request.json["password"]
        user = User.query.filter_by(email=email).first()

        user.password = new_password
        db.session.commit()

    except SignatureExpired:
        return '<h1>The token is expired!</h1>'

    return '<h1>your password has been changed</h1>'

@app.route('/forgot_password',methods=["POST"])
def forgot_password():

    email =  request.json["email"]
    try:
        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Change password', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('change_password', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({ "message": "change password email has been sent"})
    
    except :
        
        return jsonify({"error": "something went wrong"})

#TODO : check if email confirmation is working when you log in
@app.route('/login' ,methods = ['POST'])
def login_user():

    email =  request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None :
        return jsonify({"error": "unauthorized"}), 401
    
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "unauthorized"}), 401

    if user.confirmed == False:

        token = s.dumps(email, salt='email-confirm-salt-wufksk12@58')

        msg = Message('Confirm Email', sender='nekhungunifunanani9@gmail.com', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)

        mail.send(msg)

        return jsonify({"error": "confirm email first , confirm email sent"})

    session["user_id"] = user.id

    return jsonify({
        "id": user.id,
        "email": user.email,
        "domain" : user.domain,
        "confirmed": user.confirmed
    })


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

@app.route('/success', methods = ['POST'])
def success():
    
    if request.method == 'POST':

        request_msg = request.get_json()
        #print(request_msg)
        msg = request_msg['msg']
        project_id = request_msg['project_id']
        print(msg) 
        print(project_id)
        #call the function to generate response
        #response = chatFunc(data, project_id)
        response = chatFunc(msg,project_id)
        print(response)
        #return render_template('input.html', response = response , message= data )
        return {'response':response}

  


# main driver function
if __name__ == '__main__':
 

    app.run(debug=True)