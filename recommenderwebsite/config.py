import os
from dotenv import load_dotenv
from pathlib import Path

current_working_directory = Path(os.getcwd())
load_dotenv(os.path.join(current_working_directory, 'variables.env'))

class Config:
	SECRET_KEY = os.getenv("recsysSecretKey")
	SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.getenv('EMAIL')
	MAIL_PASSWORD = os.getenv('PASSWORD')

	
