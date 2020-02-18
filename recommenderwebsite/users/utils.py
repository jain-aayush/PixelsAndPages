import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from recommenderwebsite import mail


def save_picture(form_picture):
	""" Function to save the User profile picture """
	random_hex = secrets.token_hex(8) 
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext #creating a file name for the profile picture as a combination of a random_hex and the file extension
	picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn


def send_request_email(user):
	""" Function to send the change of password email at the given email address of the User """
	token = user.get_reset_token()
	msg = Message('Password Reset Request',sender = 'Project Admin<user@gmail.com>', 
		recipients = [user.email])
	msg.body = f'''To reset your password, visit following link:
{url_for('users.reset_token', token = token, _external = True)}

	If you did not make this request then simply ignore this email and no changes will be made
	'''
	mail.send(msg)