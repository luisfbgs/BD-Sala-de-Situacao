import os
import datetime
from flask import Flask, request
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client.sala_db
collection = database.news

def insert(place , title, desease):
	collection.insert({"local" : place, "titulo" : title, "doença" : desease, "mod_data" : datetime.datetime.now()})

if __name__ == "__main__":
    insert('DF', 'Aconteceu dengue', 'dengue')
    insert('Ariquemes', 'Alto índice de focos do mosquito da dengue no lixo doméstico gera', 'dengue')
    insert('PE', 'Aconteceu dengue 2', 'dengue')
    insert('RJ', 'Aconteceu dengue 3', 'dengue 2')
    insert('SP', 'Aconteceu dengue 4', 'dengue 2')
    insert('DF', 'Aconteceu dengue 5', 'dengue 3')
    insert('AM', 'Aconteceu dengue 6', 'dengue 2')
    insert('AM', 'Aconteceu dengue 7', 'dengue 5')
    insert('AM', 'Aconteceu dengue 8', 'dengue 8')
    insert('AC', 'Aconteceu dengue 9', 'dengue 9')
    insert('SC', 'Aconteceu dengue 9', 'dengue 4')
    insert('GO', 'Aconteceu dengue 9', 'dengue 7')
    insert('PA', 'Aconteceu dengue 9', 'dengue 7')
    insert('MG', 'Aconteceu dengue 9', 'dengue 8')
    insert('BA', 'Aconteceu dengue 9', 'dengue 6')
    insert('AC', 'Aconteceu dengue 9', 'dengue 1')
