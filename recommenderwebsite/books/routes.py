from flask import render_template, url_for, flash,redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from recommenderwebsite import db, gc
from recommenderwebsite.models import Book, Ratings
from recommenderwebsite.books.forms import SearchBookForm, RatingsForm

books = Blueprint('books',__name__)

@books.route('/rate_book/<int:book_id>/get_ratings',methods = ['GET','POST'])
@login_required
def get_ratings(book_id):
	form = RatingsForm()
	if(form.validate_on_submit()):
		rating = Ratings(item = 'Book',item_id = book_id,rated_by = current_user.id,
							rating = int(form.rating.data))
		db.session.add(rating)
		db.session.commit()
		return redirect(url_for('books.add_book',book_id = book_id))
	return render_template('ratings.html', form = form)


@books.route('/search_book', methods=['GET', 'POST'])
@login_required
def search_book():
	form = SearchBookForm()
	if(form.validate_on_submit()):
		try:
			search_results = gc.search_books(form.search_term.data)
			return render_template('list_books.html',books = search_results)
		except TypeError:
			flash('No Results Found', 'danger')
			return render_template('search_book.html', title='Search Book To Add', form=form)
	return render_template('search_book.html', title='Search Book To Add', form=form)


@books.route('/add_book/<int:book_id>/add', methods=['GET','POST'])
@login_required
def add_book(book_id):
	book_to_add = gc.book(book_id)
	description = book_to_add.description
	book = Book.get_or_create(book_id = book_id,title = book_to_add.title,
					 author = book_to_add.authors[0].name, description = description)
	if book not in current_user.BooksRead:
		book.ReadBy.append(current_user)
		db.session.commit()
	else:
		flash('Book Already Read!','danger')
		return redirect(url_for('users.books_read'))
	db.session.commit()
	flash('Book Added','success')
	return redirect(url_for('users.books_read'))

@books.route("/books_read/<int:book_id>/delete",methods=['POST'])
@login_required
def delete_book(book_id):
	book = Book.query.get(book_id)
	rating = Ratings.query.filter_by(item = 'Book',item_id = book_id, rated_by = current_user.id)
	current_user.BooksRead.remove(book)
	rating.delete(synchronize_session = 'evaluate')
	db.session.commit()
	flash('Book has been deleted','success')
	return redirect(url_for('users.books_read'))


