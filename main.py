import os
from flask import *
from flask_cors import CORS ,cross_origin
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from chat import chatFunc
from train import train
from  databaseModel import  db , User , Project, EmailConfig
from config import ApplicationConfig , configEmail
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
            
#todo: test the creation of intent fie when you create a new project
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

            #Todo: create a json file
            filename ="intent/"+new_project.project_id+".json"
            intent_data= open("intent/86477e97c27543f7ac24f14770f79b86.json" , "r")
            data = json.load(intent_data)
            intent_data.close()
            #add contents to the file
            save_file = open(filename,"w")
            json.dump(data ,save_file, indent=6)
            save_file.close()


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
    filename ="intent/"+project_id+".json"
    print(filename)

    if not user_id:
        return jsonify({"error":"unauthorized"}),401

    if not project_id:
        return jsonify({"error":"project does not exist"}),401

    #todo: delete this route
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
        #configure email to send verification email
        configEmail(app)
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


@app.route('/change_password/<token>', methods=['POST', 'GET'])
def change_password(token):

    if request.method == 'POST':
        
        email = s.loads(token, salt='email-confirm-salt-wufksk12@58', max_age=3600)
        new_password = request.form.get("password")
        hashedPassword = bcrypt.generate_password_hash(new_password)
        user = User.query.filter_by(email=email).first()

        user.password = hashedPassword
        db.session.commit()
        #return '<h1>password changed</h1>'


    if request.method == 'GET':

        url = f"/change_password/{token}"
        return render_template("input.html",action = url)

    return render_template("chat.html")

@app.route('/forgot_password',methods=["POST"])
def forgot_password():

    configEmail(app)
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

    # Configure Flask-Mail here
    #configure email to send verification email
    configEmail(app)
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
        project_id = request_msg['project_Id']
        print(msg) 
        print(project_id)
        #call the function to generate response
        #response = chatFunc(data, project_id)
        response = chatFunc(msg,project_id)
        print(response)
        #return render_template('input.html', response = response , message= data )
        return {'response':response}

#Todo: email route information

@app.route('/email', methods = ['POST'])
def send_email():
    #get data from form
    data = request.get_json()

    #get project id from 
    project_id = data['project_id']
    #email template
    sender_name = data['name']
    sender_email = data['email']
    sender_message = data['message']

    #get email config data of the onwer of the project from the main server
    #project_id = request.get_json(['project_id'])

    configData = EmailConfig.query.filter_by(project_id=project_id).first()

    print(configData)
    
    config_email = configData.email
    config_provider = configData.provider
    config_password = configData.password

    # Configure Flask-Mail here
    app.config['MAIL_SERVER'] = str(config_provider)
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = str(config_email)
    app.config['MAIL_PASSWORD'] = str(config_password)

    mail = Mail(app)

    

    subject= f"Message from {sender_name}"
    body= body = f"Sender's Email: {sender_email}\n\nMessage: {sender_message}"

    # Create and send the email
    msg = Message(subject=subject, sender='nekhungunifunanani9@gmail.com', recipients=['nekhungunifunanani9@gmail.com'])
    msg.body = body
    mail.send(msg)

    return 'Email sent!'

#TODO : test this routes
@app.route('/emailConfig', methods=['POST','GET','PUT','DELETE'])
def emailConfiguration():

    data = request.get_json()
    project_id = data['project_id']
    user_id =session.get("user_id")
    
    if request.method== 'GET' :
        
        configData = EmailConfig.query.filter_by(project_id=project_id).first()

        return jsonify({
            "email": configData.email,
            "provider": configData.provider,
        })
    
    if request.method== 'POST' :
        
        try:
            if not user_id:
                return jsonify({"error":"not authorized"})
            
            email = data['email']
            provider = data['provider']
            password = data['password']
            project_id = data['project_id']

            new_emailConfig = EmailConfig(email=email , provider=provider , password=password,
                        project_id=project_id, user_id=user_id
                        )
            db.session.add(new_emailConfig)
            db.session.commit()

            return jsonify({
            "email": new_emailConfig.email,
            "provider": new_emailConfig.provider
            })

        except:
            return jsonify({"error":"the was an error"})

    if request.method == 'PUT':
        data = request.get_json()
        user_id =session.get("user_id")

        try:
            if not user_id:
                return jsonify({"error":"not authorized"})
            
            email = data['email']
            provider = data['provider']
            password = data['password']
            project_id = data['project_id']

            config = EmailConfig.query.filter_by(project_id=project_id).first()
            config.email = email
            config.provider = provider
            config.password = password

            db.session.commit()


        except:
            return 404

    if request.method == "DELETE":
        try:
            config = EmailConfig.query.filter_by(project_id=project_id).first()
            db.session.delete(config)
            db.session.commit()

            return jsonify({"message": "the config has been deleted"})
        except:
            return jsonify({"error":"config  not found"})


# main driver function
if __name__ == '__main__':
 

    app.run(debug=True)