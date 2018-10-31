import os
import datetime
from flask import Flask, request
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client.sala_db
collection = database.news

def retrieve(place = "", title = "", desease = "", year = 1, month = 1, day = 1, hour = 0):
	return collection.find({"local" : {"$regex" : "^" + place},
								"titulo" : {"$regex" : "^" + title},
								"doença" : {"$regex" : "^" + desease},
								"mod_data" : {"$gte" : datetime.datetime(year, month, day, hour)}})


db_api = Flask(__name__)

@db_api.route('/retrieve', methods = ['GET'])
def teste():
	place_arg = request.args.get('place', "")
	title_arg= request.args.get('title', "")
	desease_arg = request.args.get('desease', "")
	year_arg = request.args.get('year', 1)
	month_arg = request.args.get('month', 1)
	day_arg = request.args.get('day', 1)
	hour_arg = request.args.get('hour', 0)
	return ''.join([str(item) for item in retrieve(place = place_arg, title = title_arg, desease = desease_arg, year = year_arg, month = month_arg, day = day_arg, hour = hour_arg)])

if __name__ == "__main__":
	for item in retrieve():
		print(item)
	port = int(os.environ.get('PORT', 5000))
	db_api.run(host = '0.0.0.0', port = port)
