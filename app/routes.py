from flask import Blueprint, render_template, request
from .db.moviesdb import *

main = Blueprint('main', __name__)

@main.route('/')
def index():
    data= get_movies("",1,20)
    return render_template('movies.html', title='Movies', data=data)


@main.route('/film/<film_id>')
def film_details(film_id):
    # Find the film by ID
    film =get_movie(film_id)
    return render_template('filmdetails.html', film=film)
    # return render_template('movies.html', title='Movies', data=film)

    
@main.route('/actor/<actor_name>')
def actor_details(actor_name):
    # Find the film by ID
    films =get_actor(actor_name)
    return render_template('actor.html', title=actor_name ,  data=films)
    # return render_template('movies.html', title='Movies', data=film)


@main.route('/search', methods=['GET', 'POST'])
def search_movies():
    #TO DO Build this query
    filters=request.args.get('genre')
    filters=request.args.get('year')
    films = get_movies(filters, 1, 20)
    genres= get_all_genres()
    return render_template('search.html', genre=genres, data=films)

