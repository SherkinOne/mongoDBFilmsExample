# import os

# from flask import Flask, render_template
# # from flask.json import JSONEncoder
# from flask.json.provider import DefaultJSONProvider
# from flask_cors import CORS
# ##from flask_bcrypt import Bcrypt
# ##from flask_jwt_extended import JWTManager

# from bson import json_util, ObjectId
# from datetime import datetime, timedelta

# # Flask constructor takes the name of 
# # current module (__name__) as argument.
# app = Flask(__name__)

# # The route() function of the Flask class is a decorator, 
# # which tells the application which URL should call 
# # the associated function.
# @app.route('/')
# # ‘/’ URL is bound with hello_world() function.
# def index():
#     # Fetch data from MongoDB collection
#     data=[]
#    # data = mongo.db.myCollection.find()  # Change 'myCollection' to your collection name
#     return render_template('./static/movies.html', data=data)

# # main driver function
# if __name__ == '__main__':
#     print("Here")
#     # run() method of Flask class runs the application 
#     # on the local development server.
#     app.run()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
