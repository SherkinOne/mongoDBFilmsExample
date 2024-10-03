"""
This module contains all database interfacing methods for the MFlix
application. You will be working on this file for the majority of M220P.

Each method has a short description, and the methods you must implement have
docstrings with a short explanation of the task.

Look out for TODO markers for additional help. Good luck!
"""
import bson

# from flask import current_app, g
from werkzeug.local import LocalProxy
# from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.objectid import ObjectId
from bson.errors import InvalidId

 
def get_db():
    connection_string = "mongodb://localhost:27017/"
    
    db = MongoClient(connection_string).sample_mflix 
    # if 'sample_mflix' not in g:
    #     print("Noit")
    #     db = MongoClient( connection_string).sample_mflix  # Connect to MongoDB and assign to g
    return db

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)

def get_movies_by_country(countries):
    """
    Finds and returns movies by country.
    Returns a list of dictionaries, each dictionary contains a title and an _id.
    """
    try:

        """
        Ticket: Projection

        Write a query that matches movies with the countries in the "countries"
        list, but only returns the title and _id of each movie.

        Remember that in MongoDB, the $in operator can be used with a list to
        match one or more values of a specific field.
        """

        # Find movies matching the "countries" list, but only return the title
        # and _id. Do not include a limit in your own implementation, it is
        # included here to avoid sending 46000 documents down the wire.
        print(f" c: {countries}")
        return list(db.movies.find({},{"country" : 1}))

    except Exception as e:
        return e


def get_movies_faceted(filters, page, movies_per_page):
    """
    Returns movies and runtime and ratings facets. Also returns the total
    movies matched by the filter.

    Uses the same sort_key as get_movies
    """
    sort_key = "tomatoes.viewer.numReviews"

    pipeline = []

    if "cast" in filters:
        pipeline.extend([{
            "$match": {"cast": {"$in": filters.get("cast")}}
        }, {
            "$sort": {sort_key: -1}
        }])
    else:
        raise AssertionError("No filters to pass to faceted search!")

    counting = pipeline[:]
    count_stage = {"$count": "count"}
    counting.append(count_stage)

    skip_stage = {"$skip": movies_per_page * page}
    limit_stage = {"$limit": movies_per_page}
    facet_stage = {
        "$facet": {
            "runtime": [{
                "$bucket": {
                    "groupBy": "$runtime",
                    "boundaries": [0, 60, 90, 120, 180],
                    "default": "other",
                    "output": {
                        "count": {"$sum": 1}
                    }
                }
            }],
            "rating": [{
                "$bucket": {
                    "groupBy": "$metacritic",
                    "boundaries": [0, 50, 70, 90, 100],
                    "default": "other",
                    "output": {
                        "count": {"$sum": 1}
                    }
                }
            }],
            "movies": [{
                "$addFields": {
                    "title": "$title"
                }
            }]
        }
    }

    try:
        movies = list(db.movies.aggregate(pipeline, allowDiskUse=True))[0]
        count = list(db.movies.aggregate(counting, allowDiskUse=True))[
            0].get("count")
        return (movies, count)
    except OperationFailure:
        raise OperationFailure(
            "Results too large to sort, be more restrictive in filter")


def build_query_sort_project(filters):
    """
    Builds the `query` predicate, `sort` and `projection` attributes for a given
    filters dictionary.
    """
    query = {}
    # The field "tomatoes.viewer.numReviews" only exists in the movies we want
    # to display on the front page of MFlix, because they are famous or
    # aesthetically pleasing. When we sort on it, the movies containing this
    # field will be displayed at the top of the page.
    sort = [("tomatoes.viewer.numReviews", -1)]
    project=""
    # project = {"$skip" : 20}
    if filters:
        if "text" in filters:
            query = {"$text": {"$search": filters["text"]}}
            meta_score = {"$meta": "textScore"}
            sort = [("score", meta_score)]
            project = {"score": meta_score}
        elif "cast" in filters:
            query = {"cast": {"$in": filters["cast"]}}
        elif "genres" in filters:

            """
            Ticket: Text and Subfield Search

            Given a genre in the "filters" object, construct a query that
            searches MongoDB for movies with that genre.
            """

            # TODO: Text and Subfield Search
            # Construct a query that will search for the chosen genre.
            query = {}

    return query, sort, project

def build_query_sort_project_for_search(filters):
    """
    Builds the `query` predicate, `sort` and `projection` attributes for a given
    filters dictionary.
    """
    query = {}
    # The field "tomatoes.viewer.numReviews" only exists in the movies we want
    # to display on the front page of MFlix, because they are famous or
    # aesthetically pleasing. When we sort on it, the movies containing this
    # field will be displayed at the top of the page.
    sort = [("tomatoes.viewer.numReviews", -1)]
    project = None
    genreSearch=""
    yearSearch=""
    ratingSearch=""
    query_conditions = []

# Check each filter and add to the query conditions if not None
    if filters[0] is not None:
        genreSearch = {"genres": {"$in": [filters[0]]}}
        query_conditions.append(genreSearch)

    if filters[1] is not None:
        yearSearch = {"year": filters[1]}
        query_conditions.append(yearSearch)

    if filters[2] is not None:
        ratingSearch = {"rated": filters[2]}
        query_conditions.append(ratingSearch)

# Construct the final query using $and operator if there are conditions
    if query_conditions:
        query = {"$and": query_conditions}
    else:
        query = {}  # No filters applied, can also be adjusted as needed

    return query, sort, project




def get_movies( page, movies_per_page):
    """
    Returns a cursor to a list of movie documents.
    """
 
    sort = [("tomatoes.viewer.numReviews", -1)]

    cursor = db.movies.find().sort(sort)
    
    movies = cursor.skip(page*movies_per_page).limit(movies_per_page)

    total_num_movies = db.movies.count_documents({})
    
    return (list(movies), total_num_movies)

def get_movies_from_search(filters, page, movies_per_page):
    """
    Returns a cursor to a list of movie documents.

    Based on the page number and the number of movies per page, the result may
    be skipped and limited.

    The `filters` from the API are passed to the `build_query_sort_project`
    method, which constructs a query, sort, and projection, and then that query
    is executed by this method (`get_movies`).

    Returns 2 elements in a tuple: (movies, total_num_movies)
    
    """
 
    query, sort, project = build_query_sort_project_for_search(filters)
    if project:
        cursor = db.movies.find(query, project).sort(sort)
    else:
        cursor = db.movies.find(query).sort(sort)
    total_num_movies = 0
    if page == 0:
        total_num_movies = db.movies.count_documents(query)
    else :
        movies = cursor.skip(page*movies_per_page)
 
    movies = cursor.limit(movies_per_page)

    return (list(movies), total_num_movies)


def get_movie(id):
    """
    Given a movie ID, return a movie with that ID, with the comments for that
    movie embedded in the movie document. The comments are joined from the
    comments collection using expressive $lookup.
    """
    try:
        pipeline = [
            {
                "$match": {
                    "_id": ObjectId(id)
                },
            },
          
        ]
        movie = db.movies.aggregate(pipeline).next()
        return movie

    # TODO: Error Handling
    # If an invalid ID is passed to `get_movie`, it should return None.
    except (StopIteration) as _:

        return None

    except Exception as e:
        return {}


def get_all_genres():
    """
    Returns list of all genres in the database.
    """
    return list(db.movies.aggregate([
        {"$unwind": "$genres"},
        {"$group": {"_id": None, "genres": {"$addToSet": "$genres"}}}
    ]))[0]["genres"]


def get_all_years():
    """
    Returns list of all years in the database.

    """
    return  list(db.movies.aggregate([
    {
        '$match': {
            'year': {
                '$type': 16
            }
        }
    }, {
        '$group': {
            '_id': '$year'
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }
]))


def get_all_ratings():
    """
    Returns list of all ratings in the database.

    """
    return  list(db.movies.aggregate([
    {
        '$match': {
            'rated': { "$ne" :
                None}
            }
    }, {
        '$group': {
            '_id': '$rated'
        }
    }, {
        '$sort': {
            '_id': 1
        }
    }
]))


"""
Ticket: Create/Update Comments

For this ticket, you will need to implement the following two methods:

- add_comment
- update_comment

You can find these methods below this docstring. Make sure to read the comments
to better understand the task.
"""


def add_comment(movie_id,name , email, comment, date):
    """
    Inserts a comment into the comments collection, with the following fields:

    - "name"
    - "email"
    - "movie_id"
    - "text"
    - "date"

    Name and email must be retrieved from the "user" object.
    """
    
    comment_doc = { 'movie_id' : movie_id, 'name' : name, 'email' : email,'text' : comment, 'date' : date}
    return db.comments.insert_one(comment_doc)


def update_comment(comment_id, user_email, text, date):
    """
    Updates the comment in the comment collection. Queries for the comment
    based by both comment _id field as well as the email field to doubly ensure
    the user has permission to edit this comment.
    """
    # TODO: Create/Update Comments
    # Use the user_email and comment_id to select the proper comment, then
    # update the "text" and "date" of the selected comment.
    response = db.comments.update_one(
        { "comment_id": comment_id },
        { "$set": { "text ": text, "date" : date } }
    )

    return response


def delete_comment(comment_id, user_email):
    """
    Given a user's email and a comment ID, deletes a comment from the comments
    collection
    """

    response = db.comments.delete_one( { "_id": ObjectId(comment_id) } )
    return response


def get_actor(actorName):
    """
    Given a actor name find all the films for that actor
    """
    try:
        pipeline = [
            {
               "$match": {"cast": {"$in": [actorName]}}
            },
            {
                "$project" : {"title" : 1, "year" : 1, "rated" : 1}
            }
        ]
        movies = db.movies.aggregate(pipeline) 
        return movies

    # TODO: Error Handling
    # If an invalid ID is passed to `get_movie`, it should return None.
    except (StopIteration) as _:

        return None

    except Exception as e:
        return {}



def build_query_sort_project_for_graph(filters):
    """
    Builds the `query` predicate, `sort` and `projection` attributes for a given
    filters dictionary.
    """
    query = {}
    # The field "tomatoes.viewer.numReviews" only exists in the movies we want
    # to display on the front page of MFlix, because they are famous or
    # aesthetically pleasing. When we sort on it, the movies containing this
    # field will be displayed at the top of the page.
   
    if filters:
        if  filters=="genres":
             query = [
    {
        '$match': {
            'year': {
                '$gte': 1999
            }
        }
    }, {
        '$unwind': {
            'path': '$genres'
        }
    }, {
        '$group': {
            '_id': {
                'year': '$year', 
                'genre': '$genres'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$group': {
            '_id': '$_id.genre', 
            'years': {
                '$push': {
                    'year': '$_id.year', 
                    'count': '$count'
                }
            }
        }
    }, {
        '$sort': {
             "_id":  1
        }
    }
]
        elif filters=="countries" :
            query = [
    {
        '$match': {
            'year': {
                '$gte': 1999
            }
        }
    }, {
        '$unwind': {
            'path': '$countries'
        }
    }, {
        '$group': {
            '_id': {
                'year': '$year', 
                'country': '$countries'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$group': {
            '_id': '$_id.country', 
            'years': {
                '$push': {
                    'year': '$_id.year', 
                    'count': '$count'
                }
            }
        }
    }, {
        '$sort': {
             "_id": 1
        }
    }
]
        elif "cast" in filters:
            query = {"cast": {"$in": filters["cast"]}}

            """
            Ticket: Text and Subfield Search

            Given a genre in the "filters" object, construct a query that
            searches MongoDB for movies with that genre.
            """

            # TODO: Text and Subfield Search
            # Construct a query that will search for the chosen genre.
            query = {}
    return query


def get_data_for_graph(filters):
    """
    Returns a cursor to a list of movie documents.

    Based on the page number and the number of movies per page, the result may
    be skipped and limited.

    The `filters` from the API are passed to the `build_query_sort_project`
    method, which constructs a query, sort, and projection, and then that query
    is executed by this method (`get_movies`).

    Returns 2 elements in a tuple: (movies, total_num_movies)
    
    """
    query  = build_query_sort_project_for_graph(filters)
    
    if query:
        cursor = db.movies.aggregate(query)
    #     # , project).sort(sort)
    # else:
    #     cursor = db.movies.find(query).sort(sort)
  

    return (list(cursor))


def get_data_for_graph_updated(minYear, maxYear, category, searchValues):
   #""" Take years, catgorys and return query relative to that data"""
    
    query = {}
    if category:
        if  category=="selectGenre":
             query = [
    {
        '$match': {
            'year': {
                '$gte': int(minYear)
            }
        }
    }, {
        '$unwind': {
            'path': '$genres'
        }
    }, {
        '$group': {
            '_id': {
                'year': '$year', 
                'genre': '$genres'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$group': {
            '_id': '$_id.genre', 
            'years': {
                '$push': {
                    'year': '$_id.year', 
                    'count': '$count'
                }
            }
        }
    }, {
        '$sort': {
             "_id":  1
        }
    }
]
        elif category=="countries" :
            query = [
    {
        '$match': {
            'year': {
                '$gte': 1999
            }
        }
    }, {
        '$unwind': {
            'path': '$countries'
        }
    }, {
        '$group': {
            '_id': {
                'year': '$year', 
                'country': '$countries'
            }, 
            'count': {
                '$sum': 1
            }
        }
    }, {
        '$group': {
            '_id': '$_id.country', 
            'years': {
                '$push': {
                    'year': '$_id.year', 
                    'count': '$count'
                }
            }
        }
    }, {
        '$sort': {
             "_id": 1
        }
    }
]
        # # elif "cast" in filters:
        #     query = {"cast": {"$in": filters["cast"]}}

        #     """
        #     Ticket: Text and Subfield Search

        #     Given a genre in the "filters" object, construct a query that
        #     searches MongoDB for movies with that genre.
        #     """

        #     # TODO: Text and Subfield Search
        #     # Construct a query that will search for the chosen genre.
        #     query = {}
        if query:
            cursor = db.movies.aggregate(query)
    return (list(cursor))