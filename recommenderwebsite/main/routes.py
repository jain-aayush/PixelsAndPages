from flask import render_template, request, Blueprint
from recommenderwebsite.models import Book

main = Blueprint('main',__name__)

@main.route("/")
@main.route("/home")
def home():
	""" Route for home page """
	page = request.args.get('page',1, type=int)
	books = Book.query.order_by(Book.title).paginate(page = page,per_page = 5)
	return render_template('home.html')

@main.route("/about")
def about():
	""" Route for About Page """
	return render_template('about.html', title='About')

