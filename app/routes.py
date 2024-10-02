from flask import Blueprint, render_template, request, jsonify
from .db.moviesdb import *

main = Blueprint('main', __name__)

@main.route('/' , methods=['GET', 'POST'])
def index():
    data= get_movies(1,20)
    return render_template('movies.html', title='Movies', data=data ,page=1, showTo=20)

@main.route('/page/<int:page>')
def page(page):
    data= get_movies(page,20)
    showTo = 20*page
    return render_template('movies.html', title='Movies', data=data ,page=page, showTo=showTo)


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
    return render_template('actor.html', actor_name=actor_name ,  data=films)
    # return render_template('movies.html', title='Movies', data=film)


@main.route('/search', methods=['GET', 'POST'])
def search_movies():
    #TO DO Build this query
    filters =[]
    filters.append(request.args.get('genre'))
    filters.append(request.args.get('year'))
    filters.append(request.args.get('rating'))
    if filters[1]:
        filters[1]=int(filters[1])
    genres= get_all_genres()
    years = get_all_years()
    ratings= get_all_ratings()
    films = get_movies_from_search(filters, 1, 20)
    return render_template('search.html',  filters=filters, data=films, genres=genres, years=years, ratings=ratings)

def get_genres():
    genres= get_all_genres()
    return genres

def get_years():
    years= get_all_years()
    return years

def get_ratings():
    ratings= get_all_ratings()
    return ratings

def get_all_actors():
    actors=""
    return actors

def get_all_countries():
    countries=""
    return countries

@main.route('/graphs_update', methods=['GET', 'POST'])
def get_graph_update_page():
     genres= get_all_genres()
     years = get_all_years()
     ratings= get_all_ratings()
     actors = get_all_actors()
     countries = get_all_countries()
     return render_template('graph_update.html', genres=genres, years=years, actors =actors, countries=countries, ratings=ratings)

@main.route('/graphs', methods=['GET', 'POST'])
def get_graph_page():
     return render_template('graphs.html')

@main.route('/graphdata', methods=['GET', 'POST'])
def get_graph_data():
    selected_value = request.args.get('category', default=1)
    subjects = []
    scores = []
    results =  get_data_for_graph(selected_value)
  
    return jsonify(results)

@main.route('/graphUpdate', methods=['GET', 'POST'])
def get_graph_update_data():
    json_data = request.get_json()
    maxYear= json_data['maxYear']
    minYear=json_data['minYear']
    
    categoryToSearch =json_data['category']
    values=json_data['values']
    results=""; 
    # results =  get_data_for_graph(selected_value)
  
    return jsonify(results)

