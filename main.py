from http import client
import os
import flask
from flask import *
from flask_cors import CORS ,cross_origin
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from chat import chatFunc
from train import train
from  databaseModel import  db , User , Project,Workflow, EmailConfig, googleApiConfig
from config import ApplicationConfig , configEmail
from create_mail import create_message , send_email
import json ,datetime 
from urllib.parse import urlparse
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

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
######################################################################################

#TODO: edit the formating of the email and test all api endpoints
@app.route('/sendemail' , methods=['POST'])
def test_api_request():
 
  request_data = request.get_json()

  name = request_data['name']
  email = request_data['email']
  user_message = request_data['message']
  message_sent = f'name: {name} \n'+ f'\n' + f'Email: {email}\n' + f'\n' + f'{user_message}\n' 
  project_id = request_data['project_Id']

  try:
    EmailConfigData = googleApiConfig.query.filter_by(project_id=project_id).first()
    if EmailConfigData is not None:
        pass
    else:
        return jsonify({"error": "app not configured to send emais"})
  except Exception as e:
    print(e)

  data = {'token': EmailConfigData.token,
          'refresh_token': EmailConfigData.refresh_token,
          'token_uri': EmailConfigData.token_uri,
          'client_id': EmailConfigData.client_id,
          'client_secret': EmailConfigData.client_secret,
          'scopes': [EmailConfigData.scopes]}
  #credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
  credentials = google.oauth2.credentials.Credentials(**data)
   
  print(credentials)

  drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
  print(drive)
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  #flask.session['credentials'] = credentials_to_dict(credentials)
  try:

    if EmailConfigData is not None:

        if credentials.refresh_token is not None:

            EmailConfigData.refresh_token = credentials.refresh_token
            db.session.commit()

  except Exception as e:
      print(e)


  try:
    service = drive
    sender =EmailConfigData.email 
    to =EmailConfigData.email 
    subject = name
    message_text = message_sent
    message = create_message(sender, to, subject, message_text)
    service.users().messages().send(userId='me', body=message).execute()
    
  except Exception as e:
    return f"An error occurred: {e}"

  return jsonify({"response":"email sent"}) 


@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state
  print("we at authorize")

  return flask.redirect(authorization_url)


@app.route('/oauth2callback') 
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  try:
    user_id = session.get("user_id")
    #user = flask.session['userId']
    
    print(" this user id is at oauth2callback :"+ user_id) 
    #user_id = "c9f9c2e77b0e447ba45f304b216f09ce"
    project = Project.query.filter_by(user_id=user_id).first()
    project_id = project.project_id
    #project_id = "6e86a4e67fa74268901256442ea37d09" 
    user = User.query.filter_by(id=user_id).first()
    email = user.email
    #print(user_id)
  except Exception as e :
    print(e)
    return 'error occured with the ids '

  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  #flask.session['credentials'] = credentials_to_dict(credentials)
  #credentials = credentials_to_dict(credentials)
  print(credentials)
  try:
    EmailConfigData = googleApiConfig.query.filter_by(project_id=project_id).first()

    if EmailConfigData is not None:

        if credentials.refresh_token is not None:

            EmailConfigData.refresh_token = credentials.refresh_token
            db.session.commit()

    else:
        token = credentials.token
        refresh_token = credentials.refresh_token
        token_uri = credentials.token_uri
        client_id = credentials.client_id
        client_secret = credentials.client_secret
        scopes = credentials.scopes[0]
        #email = email

        new_config = googleApiConfig(project_id=project_id,email=email,
                                        user_id=user_id,token=token,
                                        refresh_token=refresh_token,
                                        token_uri=token_uri,
                                        client_id=client_id,
                                        client_secret=client_secret,
                                        scopes=scopes)

        db.session.add(new_config)
        db.session.commit()

  except Exception as e :

      print(e)
      return 'error' 
    
  #return flask.redirect(flask.url_for('test_api_request'))
  return 'saved'
  #return redirect(url_for('save_config',token=token, refresh_token=refresh_token, token_uri=token_uri, client_id=client_id, client_secret=client_secret, scopes=scopes ))


@app.route("/@config" , methods=['GET','POST', 'DELETE'])
def delete_mail_config():
    try:
        user_id = session.get("user_id")
        #user = flask.session['userId']
        
        print("user id :"+ user_id) 
        #user_id = "c9f9c2e77b0e447ba45f304b216f09ce"
        project = Project.query.filter_by(user_id=user_id).first()
        project_id = project.project_id
        #project_id = "6e86a4e67fa74268901256442ea37d09" 
        user = User.query.filter_by(id=user_id).first()
        email = user.email
        #print(user_id)
    except Exception as e :
        print(e)

    if request.method == 'DELETE':
        EmailConfigData = googleApiConfig.query.filter_by(project_id=project_id).first()
        if EmailConfigData is not None:
            db.session.delete(EmailConfigData)
            db.session.commit()

            credentials = google.oauth2.credentials.Credentials(**EmailConfigData)
            revoke = request.post('https://oauth2.googleapis.com/revoke',
            params={'token': credentials.token},
            headers = {'content-type': 'application/x-www-form-urlencoded'})

            status_code = getattr(revoke, 'status_code')

            if status_code == 200:
                return('Credentials successfully deleted.')
            else:
                return('An error occurred while deleting, try later.')

    if request.method == 'GET':

        EmailConfigData = googleApiConfig.query.filter_by(project_id=project_id).first()
        if EmailConfigData is not None:
            return jsonify({'token': EmailConfigData.token,
            'refresh_token': EmailConfigData.refresh_token,
            'token_uri': EmailConfigData.token_uri,
            'client_id': EmailConfigData.client_id,
            'client_secret': EmailConfigData.client_secret,
            'scopes': [EmailConfigData.scopes]}) 

    return jsonify({"error":"no config "})

def credentials_to_dict(credentials): 
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}



# main driver function
if __name__ == '__main__':
 
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run('localhost', 8080)