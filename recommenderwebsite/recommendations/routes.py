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

#loading books and movies dataset
current_working_directory = Path(os.getcwd())
books = pd.read_csv(current_working_directory/'recommenderwebsite/Books.csv')
movies = pd.read_csv(current_working_directory/'recommenderwebsite/movie_dataset.csv')

def mean_vector(description_ratings):
	""" Function to compute the vector from all the Movies or Books added by the User """
	description = [list(i.keys())[0] for i in description_ratings] #list of all the description or overviews of the Books or Movies of the User
	ratings = [list(i.values())[0] for i in description_ratings] #list of all the ratings of the Books or Movies of the User
	html_tags_remover = re.compile(r'<.*?>')
	punctuations = ['.','!',';',',','?','-',':', "'",'"']
	Sum = np.zeros((1,300))
	for desc,rate in zip(description,ratings):
		desc = str(desc).lower()
		desc = html_tags_remover.sub('',desc) #removing html tags that might be present in the description 
		desc = desc.replace(' ve ',' have ')
		words = desc.split()
		new_desc_arr = []
		for word in words:
			if(word.endswith("n't")): #compact form of negative words is not present in the vocablary, dealing with this issue by expanding such words
				word = word.replace("n't",' not')
				if(word == 'ca not'):
					word = "cannot"
			word = word.replace('  ',' ')
			new_desc_arr.append(word)
		new_desc = ' '.join(new_desc_arr)
		for punc in punctuations: #removing punctuations
			new_desc = new_desc.replace(punc,' ')
		new_desc = new_desc.replace('  ',' ')
		des_sum = np.zeros((1,300))
		count = 0
		for word in new_desc.split():
			try:
				des_sum = des_sum + model[word]
				count = count + 1
			except KeyError:
				continue
		if(rate >= 3): #if rating is more than 3, it means that the User likes such content and thus add the description vector to promote similar recommendations
			Sum = Sum + (des_sum/count)
		else: #if rating is less than 3, it means that the User does not like such content and thus subtract the description vector to subdue similar recommendations
			Sum = Sum - (des_sum/count)
	Sum = Sum.reshape(300,1)
	return (Sum.reshape(300,))

@recommendations.route('/recommend_books')
@login_required
def recommend_books():
	"""" Function to recommend ten Books to the User based on Movies watched """
	if(len(current_user.MoviesWatched)>0):
		description_ratings = [] #list of dictionaries
		for movie in current_user.MoviesWatched:
			movie_rating = Ratings.query.filter_by(item = 'Movie',item_id = movie.movie_id, rated_by = current_user.id).first()
			description_ratings.append({movie.overview:movie_rating.rating})
		v1 = mean_vector(description_ratings)
		sims = [] #list to store the similarity between the mean vector and each Book in the dataset using the Euclidean Distance
		for book_vecs in book_vectors:
		    try:
		        sims.append(np.linalg.norm(book_vecs-v1)) #appending the Euclidean Distance between the vector of all Movies watched and each Book in the dataset
		    except ValueError:
		        sims.append([])
		sims = list(enumerate(sims))
		res = sorted(sims,key=lambda l:l[1])[:10] #taking the top ten most similar books
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
	"""" Function to recommend ten Movies to the User based on Books reed """
	if(len(current_user.BooksRead)>0):
		description_ratings = [] #list of dictionaries
		for book in current_user.BooksRead:
			book_rating = Ratings.query.filter_by(item = 'Book',item_id = book.book_id, rated_by = current_user.id).first()
			description_ratings.append({book.description:book_rating.rating})
		v1 = mean_vector(description_ratings)
		sims = [] #list to store the similarity between the mean vector and each Movie in the dataset using the Euclidean Distance
		for movie_vecs in movie_vectors:
		    try:
		        sims.append(np.linalg.norm(movie_vecs-v1)) #appending the Euclidean Distance between the vector of all Books read and each Movie in the dataset
		    except ValueError:
		        sims.append([])
		sims = list(enumerate(sims))
		res = sorted(sims,key=lambda l:l[1])[:10] #taking the top ten most similar books
		recommended_movies = []
		for movie in res:
			recommended_movies.append(movies.iloc[movie[0]]['title'])
		return render_template('recommendations.html', results = recommended_movies)
	else:
		flash('Add some Books so that we can recommend Movies','danger')
		return redirect(url_for('books.search_book'))	