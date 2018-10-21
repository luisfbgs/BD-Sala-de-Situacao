from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client.sala_db
collection = database.news

print("Digite o título da notícia:")
title = input()
print("Digite a doença relacionada à noticia:")
desease = input()

collection.insert({"titulo":title, "doenca":desease})

aux = collection.find()
for item in aux:
	print(item)
