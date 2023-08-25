
import os
import flask
import requests
import base64
import json
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
#from oauthfile import create_message,send_email

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = flask.Flask(__name__)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = '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'

def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] =to
    message['subject'] =subject
    message.attach(MIMEText(message_text, 'plain'))
    print("message:"+message.as_string()) 
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}
    return body 


def send_email(service, user_id, message):
    try:
        sent_message = (service.users().messages().send(userId=user_id, body=message)
                        .execute())
        print(f"Message sent. Message Id: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")

@app.route('/')
def index():
  return print_index_table()


@app.route('/test')
def test_api_request():
  #if 'credentials' not in flask.session:
  
    #return flask.redirect('authorize')

  # Load credentials from the session.
  try:
    with open("token.json", 'r') as file:
        data = json.load(file)
        print(data)
        # Check if the data is empty or no
  except (FileNotFoundError, json.JSONDecodeError):
    return flask.redirect('authorize')

  #credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
  credentials = google.oauth2.credentials.Credentials(**data)
   


  drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

  #files = drive.files().list().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  #flask.session['credentials'] = credentials_to_dict(credentials)
  credentials = credentials_to_dict(credentials) 
  with open('token.json', 'w') as token:
            json.dump(credentials , token)
  try:
    service = drive
    sender ='nekhungunifunanani9@gmail.com' 
    to ='nekhungunifunanani9@gmail.com' 
    subject = 'Test Email'
    message_text = 'This is a test email sent on your behalf using the Gmail API.'
    message = create_message(sender, to, subject, message_text)
    send_email(service, 'me', message)
  except Exception as e:
    print(f"An error occurred: {e}") 

  return 'sent' 


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
  credentials = credentials_to_dict(credentials)
  print("we at autth2callback") 

  with open('token.json', 'w') as token:
            json.dump(credentials , token) 

  return flask.redirect(flask.url_for('test_api_request'))


@app.route('/revoke') 
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.route('/clear')
def clear_credentials():
  try:
    with open("token.json", 'w') as file:
        file.write(" ")
        # Check if the data is empty or no
  except (FileNotFoundError, json.JSONDecodeError):
    return 'failde to clear credentials'
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=True)