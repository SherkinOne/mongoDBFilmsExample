from flask import Blueprint, render_template, request, jsonify
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

 

@main.route('/graphs', methods=['GET', 'POST'])
def get_graph_page():
    
     return render_template('graphs.html')

@main.route('/graphdata', methods=['GET', 'POST'])
def get_graph_data():
    selected_value = request.args.get('category', default=1)
    subjects = []
    scores = []
    results =  get_data_for_graph(selected_value)
    datasets=[]
    list_of_genres=get_all_genres()
    print(list_of_genres)
    for genre in list_of_genres : 
        for year_count in range ( 2000 ,2020) :
            for genre_by_year in results :
                print(genre_by_year)
                print(year_count)
                even_numbers = filter(lambda x: x % 2 == 0, numbers)
                print(list(even_numbers))  # Output: [2, 4, 6]
        # datasets.append({
        #     'label': f'Dataset {idx + 1}', # Label for each dataset
        #     'data': row['count'],           # Data from the count list
        #     'backgroundColor': colors[idx % len(colors)] # Cycle through colors
        # })

    return jsonify(labels=subjects, values=scores)
