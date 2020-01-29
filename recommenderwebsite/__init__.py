from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from recommenderwebsite.config import Config
from betterreads import client
from pathlib import Path
from dotenv import load_dotenv
import tmdbsimple as tmdb
import pickle
import os

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()
current_working_directory = Path(os.getcwd())
load_dotenv(os.path.join(current_working_directory, 'variables.env'))

goodreadsAPIKey = os.getenv('goodreadsAPIKey')
goodreadsAPISecret = os.getenv('goodreadsAPISecret')
gc = client.GoodreadsClient(goodreadsAPIKey,goodreadsAPISecret)

tmdb.API_KEY = os.getenv('tmdbAPIKey')

model = pickle.load(open(current_working_directory/'recommenderwebsite/word2vec.pkl','rb'))
movie_vectors = pickle.load(open(current_working_directory/'recommenderwebsite/movies_overview_vectors.pkl','rb'))
book_vectors = pickle.load(open(current_working_directory/'recommenderwebsite/books_description_vectors.pkl','rb'))

def create_app(config_class = Config):
	app = Flask(__name__)
	app.config.from_object(Config)
	print(app.secret_key)

	db.init_app(app)
	bcrypt.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)

	from recommenderwebsite.users.routes import users
	from recommenderwebsite.books.routes import books
	from recommenderwebsite.movies.routes import movies
	from recommenderwebsite.main.routes import main
	from recommenderwebsite.errors.handlers import errors
	from recommenderwebsite.recommendations.routes import recommendations

	app.register_blueprint(users)
	app.register_blueprint(books)
	app.register_blueprint(movies)
	app.register_blueprint(main)
	app.register_blueprint(errors)
	app.register_blueprint(recommendations)

	return app
