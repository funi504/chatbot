
import base64
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
        sent_message = (service.users().messages().send(userId=user_id, body=message).execute())
        
        print(f"Message sent. Message Id: {sent_message['id']}")
    except HttpError as error:
        print(f"An error occurred: {error}")
