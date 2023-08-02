import redis

class ApplicationConfig:
    SECRET_KEY = "azjEMb$hfnvn@djcbvhf123cb4d"

    SQLACHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = r"sqlite:///./db.sqlite"

    SESSION_TYPE ="redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")

    MAIL_SERVER='smtp.gmail.com'
    MAIL_USERNAME='nekhungunifunanani9@gmail.com'
    MAIL_PASSWORD='glakbsusurbxrrnr'
    MAIL_PORT=465
    MAIL_USE_SSL=True
    MAIL_USE_TLS=False