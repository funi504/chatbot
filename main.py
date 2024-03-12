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
from webscrapper import upload_data_to_vectordb 
from llm import message_reply

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
            user.confirmed = False

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
            password = request.json["password"]

            if not bcrypt.check_password_hash(user.password, password):
                return jsonify({"error": "unauthorized"}), 401
                
            db.session.delete(user)
            db.session.commit()

            return jsonify({"message": "the account has been deleted"})
        except:
            return jsonify({"error":"account not found"}), 401
            

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
        except Exception as e:
            print(e) 
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

@app.route("/workflow", methods=["POST","GET","DELETE"])
def workFlow():
    user_id =session.get("user_id")

    if request.method == 'GET':
        
        
        try:
            project = Project.query.filter_by(user_id=user_id).first()
            workflow = Workflow.query.filter_by(user_id=user_id).first()

            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            return jsonify({
                "nodes": json.loads(workflow.nodes),
                "edges": json.loads(workflow.edges)
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})

    if request.method == "POST":

        project = Project.query.filter_by(user_id=user_id).first()
        workflow = Workflow.query.filter_by(user_id=user_id).first()

        data = request.get_json()
        nodes = json.dumps(data['nodes'])
        edges = json.dumps(data['edges'])
        
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                project_id = project.project_id
                new_workflow = Workflow(user_id=user_id ,project_id=project_id, nodes=nodes, edges=edges)
                db.session.add(new_workflow)
                db.session.commit()
            
                return jsonify({
                    "nodes":json.loads(new_workflow.nodes),
                    "edges": json.loads(new_workflow.edges),
                    "message": "first workflow"
                })
            
            workflow.nodes = nodes
            workflow.edges = edges
            db.session.commit()
            print(workflow.nodes)
            return jsonify({
                    "nodes":json.loads(workflow.nodes),
                    "edges":json.loads(workflow.edges),
                    "message": "workflow updated"
                })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})

    if request.method == "DELETE":
        project = Project.query.filter_by(user_id=user_id).first()
        workflow = Workflow.query.filter_by(user_id=user_id)
        
        try:
            if not user_id:
                return jsonify({"error":"unauthorized"}),401
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            workflow = Workflow.query.filter_by(user_id=user_id).delete()
            db.session.commit()

            return jsonify({"message": "the workflow has been deleted"})
        
        except Exception as e:
            return jsonify({"error":" something went wrong, try later"})


@app.route('/upload_url_webscrapping' , methods=["POST","GET","PUT"])
def upload_url_webscrapping():

    user_id = session.get("user_id")
    project = Project.query.filter_by(user_id=user_id).first()
    project_id = project.project_id

    if not user_id:
        return jsonify({"error":"unauthorized"}),401

    if not project_id:
        return jsonify({"error":"project does not exist"}),401

    if request.method == "POST":
        request_url = request.get_json()
        #print(request_msg)
        web_url = request_url['url'] 

        upload_data_to_vectordb(web_url , project_id)

        return jsonify({"message":"uploaded"})


@app.route('/register' ,methods = ['POST'])
def register_user():
    try:
        #configure email to send verification email
        configEmail(app)
        email =  request.json["email"]
        domain = request.json["domain"]
        password = request.json["password"]
        print(email)
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

    except Exception as e :
        print(e)
        return jsonify({"error": "the was an error registering your account",})


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
    flask.session["userId"] = user.id

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

@app.route('/AIreply', methods = ['POST'])
def AIreply():
    
    if request.method == 'POST':

        request_msg = request.get_json()
        #print(request_msg)
        msg = request_msg['msg']
        project_id = request_msg['project_Id']
        print(msg) 
        print(project_id)
        #call the function to generate response
        #response = chatFunc(data, project_id)
        response = message_reply(msg , project_id)
        print(response)
        #return render_template('input.html', response = response , message= data )
        return {'response':response}

@app.route('/initialNodes', methods = ['POST'])
def initialNodes():

    if request.method == 'POST':
        
        
        try:
            data = request.get_json()
            project_id = data['projectId']
            project = Project.query.filter_by(project_id = project_id).first()
            workflow = Workflow.query.filter_by(project_id= project_id).first()
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            startConvoNodes = []
            json_nodes = json.loads(workflow.nodes)
            json_edges = json.loads(workflow.edges)

            for node in json_nodes :

                if node['type'] == 'startConvoNode':
                    connected_reply_id = []

                    for edge in json_edges:
                        if edge['source'] == node['id']:

                            connected_reply_id.append(edge['target'])

                    startConvoNodes.append({
                        'node': node,
                        'connected_reply_id': connected_reply_id 
                    })

            print(startConvoNodes)
            return jsonify({
                'data':startConvoNodes
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})

@app.route('/reply', methods = ['POST'])
def reply():

    if request.method == 'POST':
        
        try:
            data = request.get_json()
            project_id = data['projectId']
            reply_id = data['replyId']
            project = Project.query.filter_by(project_id = project_id).first()
            workflow = Workflow.query.filter_by(project_id= project_id).first()
            
            if not project:
                return jsonify({"error":"unauthorized, no project  found"}),401
            
            if not workflow : 
                return jsonify({
                    "nodes":[],
                    "edges":[]
                })
            
            replyNode = []
            json_nodes = json.loads(workflow.nodes)
            json_edges = json.loads(workflow.edges)

            for node in json_nodes :

                if node['id'] == reply_id:
                    connected_button = []
                    button_edges = []
                    parent_node = node

                    for node in json_nodes:
                        if node['type'] == 'buttonNode':
                            if node['parentNode'] == reply_id:
                                connected_button.append(node)
                                node_id = node['id']

                                for edge in json_edges:
                                    if edge['source'] == node_id:
                                        button_edges.append({
                                            'button_id' : node['id'],
                                            'edge_target': edge['target']
                                        })


                    replyNode.append({
                        'node': parent_node,
                        'connected_button': connected_button,
                        'button_edge_target': button_edges
                    })

            #print(replyNode)
            return jsonify({
                'data':replyNode
            })
            

        except Exception as e:
            print(e)
            return jsonify({"error":" something went wrong, try later"})
####################################################################################

@app.route('/email', methods = ['POST'])
def send_email():
    #get data from form
    data = request.get_json()
    try:
        print(data)
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
        body = f"Sender's Email: {sender_email}\n\nMessage: {sender_message}"

        # Create and send the email
        #msg = Message(subject=subject, sender='nekhungunifunanani9@gmail.com', recipients=['nekhungunifunanani9@gmail.com'])
        msg = Message(subject=subject, sender= config_email , recipients=[ config_email ])
        msg.body = body
        mail.send(msg)

        return jsonify({"response":"email sent"})
    except Exception as e :

        return jsonify({"response": e })
        

@app.route('/emailConfig', methods=['POST','GET','PUT','DELETE'])
def emailConfiguration():

    data = request.get_json()
    project_id = data['project_id']
    user_id =session.get("user_id")
    
    if request.method== 'GET' :
        
        configData = EmailConfig.query.filter_by(project_id=project_id).first()
        if not configData:
            return jsonify({'error':'config not found'}),401
        return jsonify({
            "email": configData.email,
            "provider": configData.provider,
            "projectId": project_id
        })
    
    if request.method== 'POST' :
        
        try:
            if not user_id:
                return jsonify({"error":"not authorized"}),401
            
            email = data['email']
            provider = data['provider']
            password = data['password']
            project_id = data['project_id']
            config = EmailConfig.query.filter_by(project_id=project_id).first()
            project = Project.query.filter_by(project_id = project_id).first()

            if not project:
                return jsonify({"error":"not authorized"}),401

            if not config:
                new_emailConfig = EmailConfig(email=email , provider=provider , password=password,
                            project_id=project_id, user_id=user_id
                            )
                db.session.add(new_emailConfig)
                db.session.commit()

                return jsonify({
                "email": new_emailConfig.email,
                "provider": new_emailConfig.provider
                })
            

            config = EmailConfig.query.filter_by(project_id=project_id).first()
            config.email = email
            config.provider = provider
            config.password = password

            db.session.commit()

            return jsonify({
                "email": config.email,
                "provider": config.provider
                })
        except:
            return jsonify({"error":"the was an error"}),404

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
######################################################################################


# main driver function
if __name__ == '__main__':
 
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080)