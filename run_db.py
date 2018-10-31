import datetime
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client.sala_db
collection = database.news

print("Digite o título da notícia:")
title = input()
print("Digite a doença relacionada à noticia:")
desease = input()
print("Digite o local relacionado à doença:")
place = input()

collection.insert({"titulo" : title, "doença" : desease, "mod_data" : datetime.datetime.now(), "local" : place})

for item in collection.find():
	print(item)
