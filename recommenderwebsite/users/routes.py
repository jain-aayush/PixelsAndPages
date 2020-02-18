from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from recommenderwebsite import db, bcrypt
from recommenderwebsite.models import User, Book
from recommenderwebsite.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from recommenderwebsite.users.utils import save_picture, send_request_email


users = Blueprint('users',__name__)

@users.route("/login", methods = ['GET','POST'])
def login():
	""" Route for User Login """
	form = LoginForm()
	if(form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		if(user and bcrypt.check_password_hash(user.password, form.password.data)):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')
			if(next_page):
				return redirect(next_page)
			else:
				return redirect(url_for('main.home'))
		else:
			flash('Incorrect Username/Password', 'danger')
	return render_template('login.html', title = 'Login', form = form)

@users.route("/register", methods = ['GET','POST'])
def register():
	""" Route for registration of new Users """
	form = RegistrationForm()
	if(form.validate_on_submit()):
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(fullname=form.fullname.data, username = form.username.data,
			password = hashed_password,email = form.email.data)
		db.session.add(user)
		db.session.commit()
		flash(f'Account Successfully Created for {form.fullname.data}! You can login now','success')
		return 	redirect(url_for('users.login'))
	return render_template('register.html', title = 'Sign-Up', form = form)

@users.route('/logout')
def logout():
	""" Route to logout the current User """
	logout_user()
	flash('You have been logged out Successfully!', 'success')
	return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	""" Route to display the accouts page of the logged-in User """
	form = UpdateAccountForm()
	if(request.method == 'POST'):
		if(form.validate_on_submit()):
			if(form.picture.data):
				picture_file = save_picture(form.picture.data)
				current_user.image_file = picture_file
			current_user.fullname = form.fullname.data
			current_user.username = form.username.data
			current_user.email = form.email.data
			db.session.commit()
			flash('Account Updated!', 'success')
			return redirect(url_for('users.account'))
	elif(request.method == 'GET'):
		form.fullname.data = current_user.fullname
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/'+current_user.image_file)
	return render_template('account.html', title='Account', 
		image_file = image_file, form = form)

@users.route('/books_read', methods=['GET','POST'])
@login_required
def books_read():
	""" Route to list the Books Read by the User """
	books = current_user.BooksRead
	return render_template('books_read.html', title = 'Books Read', books = books)

@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
	""" Route to allow User for a change in account password """
	if(current_user.is_authenticated):
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if(form.validate_on_submit()):
		user = User.query.filter_by(email = form.email.data).first()
		send_request_email(user)
		flash('An Email has been sent with instructions to reset your password')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', title = 'Reset Password', form=form)

@users.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
	""" Route to allow the User to reset their account password after requesting a change in password """
	if(current_user.is_authenticated):
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token','warning')
		return redirect(url_for('users.reset_request'))
	form = ResetPasswordForm()
	if(form.validate_on_submit()):
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated. You can login now','success')
		return 	redirect(url_for('users.login'))
	return render_template('reset_token.html',title = 'Reset Password',form=form)

@users.route('/movies_watched', methods=['GET','POST'])
@login_required
def movies_watched():
	""" Route to list the movies read by the User """
	movies = current_user.MoviesWatched
	return render_template('movies_watched.html', title = 'Movies Watched', movies = movies)
