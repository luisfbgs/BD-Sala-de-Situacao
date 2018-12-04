#!/usr/bin/env python3
# -*- coding: utf-8 -

import os
import datetime
import json
import tablib
from bson.json_util import dumps
from bson.json_util import loads
from bson.objectid import ObjectId
from flask import Flask, request, jsonify, Response, render_template, flash
from wtforms import Form, TextField, TextAreaField, StringField, SubmitField, BooleanField, validators
from pymongo import MongoClient
from convert_country import name_country_sig, sig_country_name
from convert_state import name_state_sig, sig_state_name

client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
database = client.sala_db
collection = database.news

db_api = Flask(__name__)
db_api.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

def correct_local(local):
    country, region = local
    if region in name_country_sig:
        country = name_country_sig[region]
    if region in sig_country_name:
        country = region
    elif country in name_country_sig:
        country = name_country_sig[country]
    if region in name_state_sig:
        country = 'BR'
        region = name_state_sig[region]
    elif region in sig_state_name:
        country = 'BR'
    return (country, region)


def retrieve_query(content="", local=("", ""), title="", disease="", date=(1, 1, 1, 0)):
    """Requests and returns the list of documents in the database
     with prefixs that match the arguments"""
    year, month, day, hour = date
    country, region = correct_local(local)
    return collection.find({"title" : {"$regex" : "^" + title},
                            "country" : {"$regex" : "^" + country},
                            "content" : {"$regex" : "^" + content},
                            "region" : {"$regex" : "^" + region},
                            "disease" : {"$regex" : "^" + disease},
                            "mod_date" : {"$gte" : datetime.datetime(year, month, day, hour)}})

def insert_query(json_content):
    """Inserts the json document in the database with a modification date attached.
    Returns the ID of the new document in the database"""
    json_content['country'], json_content['region'] = correct_local((json_content['country'], json_content['region']))
    new_id = collection.insert_one(json_content).inserted_id
    collection.update_one({'_id' : new_id}, {'$set' : {'mod_date' : datetime.datetime.now()}})
    return new_id

def check_input_json(input_json):
    """Checks if the recieved json contains the required fields"""
    keys = ['source', 'author', 'title', 'description', 'url',
            'url_to_image', 'country', 'region', 'score', 'date', 'disease']
    for k in keys:
        assert k in input_json

@db_api.route('/retrieve', methods=['GET'])
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
    query_json = dumps(query_str)
    return jsonify(json.loads(query_json))

@db_api.route('/insert', methods=['GET'])
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
    except:
        return "Fail"
    return str(insert_query(json_content))

@db_api.route('/delete', methods=['GET'])
def delete():
    index = request.args.get('index', "")
    key = request.args.get('key', "")
    if key != os.environ['INSERT_KEY']:
        return "Fail: incorrect key"
    try:
        qry = collection.find({'_id' : ObjectId(index)})
        if len(str(qry)) == 0:
            return "Fail: desired id not found"
    except:
        return "Fail"
    collection.delete_one({'_id' : ObjectId(index)})
    return "Success"

@db_api.route('/update', methods=['GET'])
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
        qry = collection.find({'_id' : ObjectId(index)})
        if len(str(qry)) == 0:
            return "Fail: desired id not found"
    except:
        return "Fail"
    collection.update_one({'_id' : ObjectId(index)}, {'$set' : {'mod_date' : datetime.datetime.now(), field : content}})
    qry = collection.find({'_id' : ObjectId(index)})
    return jsonify(json.loads(dumps(qry)))

class ReusableForm(Form):
    author   = TextField('Autor:', default = "")
    source   = TextField('Fonte:', default = "")
    title   = TextField('Título:', default = "")
    description   = TextField('Descrição:', default = "")
    url   = TextField('Url:', default = "")
    url_to_image   = TextField('Url da imagem:', default = "")
    country = TextField('País:', default = "")
    region  = TextField('Região:', default = "")
    score  = TextField('Pontuação:', default = "")
    content = TextField('Conteúdo:', default = "")
    disease = TextField('Doença:', default = "") 
    date = TextField('Data de publicação:', default = "") 
    password = TextField('Senha de insersão:', default = "") 
    show_author       = BooleanField('Mostrar Autor', false_values=('false', ''))
    show_title        = BooleanField('Mostrar Título', false_values=('false', ''))
    show_source       = BooleanField('Mostrar Fonte', false_values=('false', ''))
    show_url          = BooleanField('Mostrar Url', false_values=('false', ''))
    show_url_to_image = BooleanField('Mostrar Url da imagem', false_values=('false', ''))
    show_content      = BooleanField('Mostrar Conteúdo', false_values=('false', ''))
    show_disease      = BooleanField('Mostrar Doença', false_values=('false', ''))
    show_country      = BooleanField('Mostrar País', false_values=('false', ''))
    show_region       = BooleanField('Mostrar Região', false_values=('false', ''))
    show_published_at = BooleanField('Mostrar Data de Publicação', false_values=('false', ''))
    submit = SubmitField('Download')
    submiti = SubmitField('Enviar')


@db_api.route("/busca", methods=['GET', 'POST'])
def search_page():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        title = request.form['title']
        country = request.form['country']
        region = request.form['region']
        content = request.form['content']
        disease = request.form['disease']

        query_str = retrieve_query(content, (country, region), title, disease)
        query_json = json.loads(dumps(query_str))
        csv = 'Id'
        if 'show_author' in request.form:
            csv += ',Autor'
        if 'show_title' in request.form:
            csv += ',Título'
        if 'show_source' in request.form:
            csv += ',Fonte'
        if 'show_url' in request.form:
            csv += ',Url'
        if 'show_url_to_image' in request.form:
            csv += ',Url da imagem'
        if 'show_content' in request.form:
            csv += ',Conteúdo'
        if 'show_disease' in request.form:
            csv += ',Doença'
        if 'show_country' in request.form:
            csv += ',País'
        if 'show_region' in request.form:
            csv += ',Região'
        if 'show_published_at' in request.form:
            csv += ',Data de Publicação'
        csv += '\r\n'
        for item in query_json:
            csv += "\"" + str(item['_id']['$oid']) + "\""
            if 'show_author' in request.form:
                csv += ",\"" + str(item['author']) + "\""
            if 'show_title' in request.form:
                csv += ",\"" + str(item['title']) + "\""
            if 'show_source' in request.form:
                csv += ",\"" + str(item['source']) + "\""
            if 'show_url' in request.form:
                csv += ",\"" + str(item['url']) + "\""
            if 'show_url_to_image' in request.form:
                csv += ",\"" + str(item['url_to_image']) + "\""
            if 'show_content' in request.form:
                csv += ",\"" + str(item['content']) + "\""
            if 'show_disease' in request.form:
                csv += ",\"" + str(item['disease']) + "\""
            if 'show_country' in request.form:
                csv += ",\"" + str(item['country']) + "\""
            if 'show_region' in request.form:
                csv += ",\"" + str(item['region']) + "\""
            if 'show_published_at' in request.form:
                csv += ",\"" + str(item['published_at']) + "\""
            csv += '\r\n'
        return Response(
            csv,
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=news.csv"})    
 
    return render_template('retrieve.html', form=form)

@db_api.route("/inserir", methods=['GET', 'POST'])
def insert_page():
    form = ReusableForm(request.form)
    if request.method == 'POST':
        author = request.form['author']
        source = request.form['source']
        title = request.form['title']
        description = request.form['description']
        url = request.form['url']
        url_to_image = request.form['url_to_image']
        country = request.form['country']
        region = request.form['region']
        score = request.form['score']
        content = request.form['content']
        disease = request.form['disease']
        date = request.form['date']
        password = request.form['password']

        if password != os.environ['INSERT_KEY']:
            flash("Senha incorreta")

        else:
            insert_json = ("{\"source\": \"" + source + "\","
                            + "\"author\": \"" + author + "\","
                            + "\"title\": \"" + title + "\","
                            + "\"description\": \"" + description + "\","
                            + "\"url\": \"" + url + "\","
                            + "\"url_to_image\": \"" + url_to_image + "\","
                            + "\"country\": \"" + country + "\","
                            + "\"region\": \"" + region + "\","
                            + "\"score\": \"" + score + "\","
                            + "\"published_at\": \"" + date + "\","
                            + "\"content\": \"" + content + "\","
                            + "\"disease\": \"" + disease + "\""
                            + "}")
            res = insert_query(loads(insert_json))
            flash(str(res))
 
    return render_template('insert.html', form=form)

@db_api.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    db_api.run(host='0.0.0.0', port=port)
