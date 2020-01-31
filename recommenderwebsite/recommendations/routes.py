from flask import Blueprint, render_template,redirect, url_for,flash
from flask_login import login_required, current_user
from recommenderwebsite import model, movie_vectors, book_vectors
from recommenderwebsite.models import Ratings
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from pathlib import Path
import pandas as pd
import numpy as np 
import re
import os

recommendations = Blueprint('recommendations',__name__)

current_working_directory = Path(os.getcwd())
books = pd.read_csv(current_working_directory/'recommenderwebsite/Books.csv')
movies = pd.read_csv(current_working_directory/'recommenderwebsite/movie_dataset.csv')

def mean_vector(description_ratings):
	description = [list(i.keys())[0] for i in description_ratings]
	ratings = [list(i.values())[0] for i in description_ratings]
	overall_rating = sum(ratings)
	average_rating = overall_rating/len(ratings)
	description = ' '.join(description)
	regex = re.compile('[^a-z \n]')
	description = regex.sub('',description)
	Sum = np.zeros((1,300))
	for des,rate in zip(description,ratings):
		des_sum = np.zeros((1,300))
		count = 0
		for word in des.split():
			try:
				des_sum = des_sum + model[word]
				count = count + 1
			except KeyError:
				continue
		if(len(ratings) == 1):
			Sum = Sum + ((des_sum/count)*rate)
		else:
			if(rate - average_rating >= 0):
				Sum = Sum + ((des_sum/count) * ((rate - average_rating) + rate))
			elif(average_rating - rate > 1.2):
				Sum = Sum - ((des_sum/count) * ((average_rating - rate) + rate))
			else:
				Sum = Sum - ((des_sum/count))
	Sum = Sum.reshape(300,1)
	Sum = np.nan_to_num(Sum)
	Sum = normalize(Sum,axis=0)
	return (Sum.reshape(300,))

@recommendations.route('/recommend_books')
@login_required
def recommend_books():
	if(len(current_user.MoviesWatched)>0):
		description_ratings = []
		for movie in current_user.MoviesWatched:
			movie_rating = Ratings.query.filter_by(item = 'Movie',item_id = movie.movie_id, rated_by = current_user.id).first()
			description_ratings.append({movie.overview:movie_rating.rating})
		v1 = mean_vector(description_ratings)
		sims = []
		for book_vecs in book_vectors:
		    try:
		        sims.append(np.linalg.norm(book_vecs-v1))
		    except ValueError:
		        sims.append([])
		sims = list(enumerate(sims))
		res = sorted(sims,key=lambda l:l[1])[:10]
		recommended_books = []
		for book in res:
			recommended_books.append(books.iloc[book[0]]['title'])
		return render_template('recommendations.html', results = recommended_books)
	else:
		flash('Add some Movies so that we can recommend Books','danger')
		return redirect(url_for('movies.search_movie'))

@recommendations.route('/recommend_movies')
@login_required
def recommend_movies():
	if(len(current_user.BooksRead)>0):
		description_ratings = []
		for book in current_user.BooksRead:
			book_rating = Ratings.query.filter_by(item = 'Book',item_id = book.book_id, rated_by = current_user.id).first()
			description_ratings.append({book.description:book_rating.rating})
		v1 = mean_vector(description_ratings)
		sims = []
		for movie_vecs in movie_vectors:
		    try:
		        sims.append(np.linalg.norm(movie_vecs-v1))
		    except ValueError:
		        sims.append([])
		sims = list(enumerate(sims))
		res = sorted(sims,key=lambda l:l[1])[:10]
		recommended_movies = []
		for movie in res:
			recommended_movies.append(movies.iloc[movie[0]]['title'])
		return render_template('recommendations.html', results = recommended_movies)
	else:
		flash('Add some Books so that we can recommend Movies','danger')
		return redirect(url_for('books.search_book'))	