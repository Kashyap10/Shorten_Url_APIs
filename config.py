import os
from dotenv import load_dotenv

load_dotenv()

class Config(object):
    """
    This clas is containing secretkey and databse url of postgres
    """
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
