import os
import datetime
from flask import Flask, request
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client.sala_db
collection = database.news

db_api = Flask(__name__)

def retrieve_query(place = "", title = "", desease = "", year = 1, month = 1, day = 1, hour = 0):
	return collection.find({"local" : {"$regex" : "^" + place},
			"titulo" : {"$regex" : "^" + title},
			"doença" : {"$regex" : "^" + desease},
			"mod_data" : {"$gte" : datetime.datetime(year, month, day, hour)}})

def insert_query(place , title, desease):
	collection.insert({"local" : place, "titulo" : title, "doença" : desease, "mod_data" : datetime.datetime.now()})

@db_api.route('/retrieve', methods = ['GET'])
def retrieve():
	place = request.args.get('place', "")
	title = request.args.get('title', "")
	desease = request.args.get('desease', "")
	year = request.args.get('year', 1)
	month = request.args.get('month', 1)
	day = request.args.get('day', 1)
	hour = request.args.get('hour', 0)
	return ''.join([str(item) for item in retrieve_query(place, title, desease, year, month, day, hour)])

@db_api.route('/insert', methods = ['GET'])
def insert():
	place = request.args.get('place', "")
	title = request.args.get('title', "")
	desease = request.args.get('desease', "")
	if place == "" or title == "" or desease == "":
		return "Fail"
	insert_query(place, title, desease)
	return "Success"

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	db_api.run(host = '0.0.0.0', port = port)
