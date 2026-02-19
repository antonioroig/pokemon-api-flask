import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")

    SQLALCHEMY_DATABASE_URI = os.environ.get("POSTGRES_URL")

    WTF_CSRF_ENABLED = False
