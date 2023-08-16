import redis
from flask_mail import Mail, Message

def configEmail(app):

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'nekhungunifunanani9@gmail.com'
    app.config['MAIL_PASSWORD'] = 'glakbsusurbxrrnr'

    mail = Mail(app)
    
class ApplicationConfig:
    SECRET_KEY = "azjEMb$hfnvn@djcbvhf123cb4d"

    SQLACHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    SESSION_TYPE ="redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")

    #MAIL_SERVER='smtp.gmail.com'
    #MAIL_USERNAME='nekhungunifunanani9@gmail.com'
    #MAIL_PORT=465
    #MAIL_USE_SSL=True
    #MAIL_USE_TLS=False