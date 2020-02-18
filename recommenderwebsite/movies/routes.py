from flask import render_template,flash,redirect, url_for,Blueprint
from flask_login import current_user, login_required
from recommenderwebsite import tmdb , db
from recommenderwebsite.models import Movie, Ratings
from recommenderwebsite.movies.forms import SearchMovieForm, RatingsForm

movies = Blueprint('movies', __name__)

@movies.route('/rate_movie/<int:movie_id>/get_ratings',methods = ['GET','POST'])
@login_required
def get_ratings(movie_id):
	""" Route to get the Users rating of the Movie """
	form = RatingsForm()
	if(form.validate_on_submit()):
		rating = Ratings(item = 'Movie',item_id = movie_id,rated_by = current_user.id
							,rating = int(form.rating.data))
		db.session.add(rating)
		db.session.commit()
		return redirect(url_for('movies.add_movie',movie_id = movie_id))
	return render_template('ratings.html', form = form)

@movies.route('/search_movie', methods=['GET', 'POST'])
@login_required
def search_movie():
	""" Route to ask the User for the Movie he wants to search and then displaying the result """
	form = SearchMovieForm()
	if(form.validate_on_submit()):
		search = tmdb.Search()
		search.movie(query = form.search_term.data) #using the tmdb api to search for movies
		if(search.results):
			return render_template('list_movies.html', movies = search.results)
		else:
			flash('No Movies Found!', 'danger')
			return render_template('search_movie.html', title = 'Search Movie To Add', form = form)
	return render_template('search_movie.html', title = 'Search Movie To Add', form = form)

@movies.route('/add_movie/<int:movie_id>/add', methods=['GET','POST'])
@login_required
def add_movie(movie_id):
	""" Route to add a Book to the list of books read by an User """
	movie_to_add = tmdb.Movies(movie_id)
	response = movie_to_add.info()
	crew = movie_to_add.credits()['crew']
	director = ''
	for member in crew:
		if(member['job'] == 'Director'):
			director = member['name']
			break
	movie = Movie.get_or_create(movie_id = movie_id,title = movie_to_add.title,
				director = director, overview = movie_to_add.overview)
	if movie not in current_user.MoviesWatched:
		movie.WatchedBy.append(current_user)
		db.session.commit()
	else:
		flash('Already watched!','danger')
		return redirect(url_for('users.movies_watched'))
	db.session.commit()
	flash('Movie Added','success')
	return redirect(url_for('users.movies_watched'))

@movies.route("/movies_watched/<int:movie_id>/delete",methods=['POST'])
@login_required
def delete_movie(movie_id):
	""" Route to remove a book from the list of books read by a User """
	movie = Movie.query.filter_by(movie_id = movie_id).first()
	rating = Ratings.query.filter_by(item = 'Movie',item_id = movie_id, rated_by = current_user.id)
	current_user.MoviesWatched.remove(movie)
	rating.delete(synchronize_session = 'evaluate')
	db.session.commit()
	flash('Movie has been deleted','success')
	return redirect(url_for('users.movies_watched'))

		