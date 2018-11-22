import os
import urllib.request
import json
import tablib
from flask import Flask, Response, render_template, flash, request, jsonify
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class ReusableForm(Form):
    title   = TextField('Título:', default = "")
    country = TextField('País:', default = "")
    region  = TextField('Região:', default = "")
    content = TextField('Conteúdo:', default = "")
    disease = TextField('Doença:', default = "") 
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = ReusableForm(request.form)
 
    print (form.errors)
    if request.method == 'POST':
        title = request.form['title']
        country = request.form['country']
        region = request.form['region']
        content = request.form['content']
        disease = request.form['disease']
 
        if form.validate():
            request_url = ('https://sala-de-situacao-bd.herokuapp.com/retrieve?' +
                           'title=' + title +
                           '&country=' + country +
                           '&region=' + region +
                           '&content=' + region +
                           '&disease=' + disease)
            api_data = urllib.request.urlopen(request_url)
            api_json = json.loads(api_data.read().decode('utf-8'))
            csv = 'Autor,Título,Fonte,Url,Url da imagem,Conteúdo,Doença,País,Região\r\n'
            for item in api_json:
                csv += "\"" + str(item['author']) + "\""
                csv += ",\"" + str(item['title']) + "\""
                csv += ",\"" + str(item['source']) + "\""
                csv += ",\"" + str(item['url']) + "\""
                csv += ",\"" + str(item['url_to_image']) + "\""
                csv += ",\"" + str(item['content']) + "\""
                csv += ",\"" + str(item['disease']) + "\""
                csv += ",\"" + str(item['country']) + "\""
                csv += ",\"" + str(item['region']) + "\""
                csv += '\r\n'
            # dataset = tablib.Dataset()
            # dataset.csv = csv
            return Response(
                csv,
                mimetype="text/csv",
                headers={"Content-disposition":
                         "attachment; filename=news.csv"})    
            # return dataset.html
        else:
            flash('Alguma coisa deu errado.')
 
    return render_template('retrieve.html', form=form)
 
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
