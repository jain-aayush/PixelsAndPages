from recommenderwebsite import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

association_books = db.Table('association_books', db.Model.metadata,
    db.Column('Book_id', db.Integer, db.ForeignKey('book.book_id')),
    db.Column('Reader_id', db.Integer, db.ForeignKey('user.id'))
)

association_movies = db.Table('association_movies', db.Model.metadata,
	db.Column('Movie_id', db.Integer, db.ForeignKey('movie.movie_id')),
    db.Column('Watcher_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(50), nullable=False)
	username = db.Column(db.String(30), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	BooksRead = db.relationship('Book', secondary = association_books, backref = 'ReadBy',lazy=True)
	MoviesWatched = db.relationship('Movie', secondary = association_movies, backref='WatchedBy', lazy=True)
	
	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id':self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)		

	def __repr__(self):
		return f"User('{self.fullname}','{self.username}', '{self.email}', '{self.image_file}')"


class Book(db.Model):
	__tablename__ = 'book'
	book_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(50), nullable=False)
	author = db.Column(db.String(50), nullable=False)
	description = db.Column(db.Text)

	def get_or_create(book_id,title,author,description):
		exists = db.session.query(Book.book_id).filter_by(book_id=book_id).scalar() is not None
		if exists:
			return Book.query.get(book_id)
		return Book(book_id=book_id, title = title, author = author,description = description)

	def __repr__(self):
		return f"Book('{self.title}', '{self.author}')"

class Movie(db.Model):
	__tablename__ = 'movie'
	movie_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	director = db.Column(db.String(50), nullable=False)
	overview = db.Column(db.Text)

	def get_or_create(movie_id,title,director,overview):
		exists = db.session.query(Movie.movie_id).filter_by(movie_id=movie_id).scalar() is not None
		if exists:
			return Movie.query.get(movie_id)
		return Movie(movie_id=movie_id, title = title, director = director,overview = overview)

	def __repr__(self):
		return f"Movie('{self.title}', '{self.director}')"

class Ratings(db.Model):
	__tablename__ = 'ratings'
	ratings_id = db.Column(db.Integer, primary_key=True)
	item = db.Column(db.String(5),nullable = False)
	item_id = db.Column(db.Integer, nullable = False)
	rated_by = db.Column(db.Integer, nullable = False)
	rating = db.Column(db.Integer, nullable = False)