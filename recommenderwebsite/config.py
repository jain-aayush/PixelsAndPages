import os

class Config:
	SECRET_KEY = os.getenv("recsysSecretKey")
	SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.getenv('EMAIL')
	MAIL_PASSWORD = os.getenv('PASSWORD')

	