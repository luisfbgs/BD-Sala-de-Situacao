import os
import datetime
import json
from bson.json_util import dumps
from bson.json_util import loads
from flask import Flask, request, jsonify
from pymongo import MongoClient

CLIENT = MongoClient('mongodb+srv://adm_sala_st:' + os.environ['DB_PASS'] + os.environ['CLUSTER_U'])
DATABASE = CLIENT.sala_db
COLLECTION = DATABASE.news

DB_API = Flask(__name__)

def retrieve_query(content="", local=("", ""), title="", disease="", date=(1, 1, 1, 0)):
    """Requests and returns the list of documents in the database
     with prefixs that match the arguments"""
    year, month, day, hour = date
    country, region = local
    return COLLECTION.find({"title" : {"$regex" : "^" + title},
                            "country" : {"$regex" : "^" + country},
                            "content" : {"$regex" : "^" + content},
                            "region" : {"$regex" : "^" + region},
                            "disease" : {"$regex" : "^" + disease},
                            "mod_date" : {"$gte" : datetime.datetime(year, month, day, hour)}})

def insert_query(json_content):
    """Inserts the json document in the database with a modification date attached.
    Returns the ID of the new document in the database"""
    new_id = COLLECTION.insert_one(json_content).inserted_id
    COLLECTION.update_one({'_id' : new_id}, {'$set' : {'mod_date' : datetime.datetime.now()}})
    return new_id

def check_input_json(input_json):
    """Checks if the recieved json contains the required fields"""
    keys = ['source', 'author', 'title', 'description', 'url',
            'url_to_image', 'country', 'region', 'score', 'date', 'disease']
    for k in keys:
        assert k in input_json

@DB_API.route('/retrieve', methods=['GET'])
def retrieve():
    """Requests the desired documents from the database"""
    country = request.args.get('country', "")
    region = request.args.get('region', "")
    title = request.args.get('title', "")
    content = request.args.get('content', "")
    disease = request.args.get('disease', "")
    year = int(request.args.get('year', 1))
    month = int(request.args.get('month', 1))
    day = int(request.args.get('day', 1))
    hour = int(request.args.get('hour', 0))

    query_str = retrieve_query(content, (country, region), title, disease, (year, month, day, hour))
    query_str = dumps(query_str)
    return jsonify(json.loads(query_str))

@DB_API.route('/insert', methods=['GET'])
def insert():
    """Inserts the desired document in the database.
    Returns the document ID if the insertion is successful or 'Fail' otherwise"""
    content = request.args.get('json', "")
    key = request.args.get('key', "")
    if key != os.environ['INSERT_KEY']:
        return "Fail: incorrect key"
    try:
        json_content = loads(content)
        check_input_json(json_content)
    except AssertionError as error:
        return "Fail: " + str(error)
    return str(insert_query(json_content))

@DB_API.route('/update', methods=['GET'])
def update():
    index = request.args.get('index', "")
    field = request.args.get('field', "")
    content = request.args.get('content', "")
    key = request.args.get('key', "")
    if key != os.environ['INSERT_KEY']:
        return "Fail: incorrect key"
    fields = ['source', 'author', 'title', 'description', 'url',
            'url_to_image', 'country', 'region', 'score', 'date', 'disease']
    if not (field in fields):
        return "Fail: the desired field cannot be updated"
    try:
        qry = COLLECTION.find({'_id' : index})
        if len(qry) == 0:
            return "Fail: desired id not found"
        return "Test"
    except AssertionError as error:
        return "except " + str(error)
    return "Sucess"
    COLLECTION.update_one({'_id' : index}, {'$set' : {'mod_date' : datetime.datetime.now(), field : content}})
    return str(qry)

if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5000))
    DB_API.run(host='0.0.0.0', port=PORT)
