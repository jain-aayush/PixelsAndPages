from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from recommenderwebsite.models import User


class RegistrationForm(FlaskForm):
	fullname = StringField('Full Name', validators = [DataRequired()])
	username = StringField('Username', validators = [DataRequired(), Length(min=2,max = 30)])
	gender = RadioField('Gender', choices = [('M','Male'),('F','Female'),('O','Other')], default = 'M')
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		""" Check if a User with the same username already exists """
		user = User.query.filter_by(username = username.data).first()
		if(user):
			raise ValidationError('Username already exists!')

	def validate_email(self, email):
		""" Check if the User is already registered with the given email id """
		user = User.query.filter_by(email = email.data).first()
		if(user):
			raise ValidationError('Email already used!')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
	fullname = StringField('Fullname', validators=[DataRequired()])
	username = StringField('Username', validators = [DataRequired(), Length(min=2,max = 30)])
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if(username.data != current_user.username):
			user = User.query.filter_by(username = username.data).first()
			if(user):
				raise ValidationError('Username already exists!')

	def validate_email(self, email):
		if(email.data != current_user.email):
			user = User.query.filter_by(email = email.data).first()
			if(user):
				raise ValidationError('Email already used!')

class RequestResetForm(FlaskForm):
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')
	def validate_email(self, email):
		user = User.query.filter_by(email = email.data).first()
		if user is None:
			raise ValidationError('There is no account with that email. You must register first!')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')