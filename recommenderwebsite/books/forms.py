from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired

class SearchBookForm(FlaskForm):
	search_term = StringField('Title/Author Name', validators=[DataRequired()])
	submit = SubmitField('Search')

class RatingsForm(FlaskForm):
	rating = RadioField('Rating', choices = [('1','Rating 1'),('2','Rating 2'),('3','Rating 3'),('4','Rating 4'),('5','Rating 5')], default = '1')
	submit = SubmitField('Submit Rating')
