import urllib.request
import json
from flask import Flask, render_template, flash, request, jsonify
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

            return jsonify(api_json)
        else:
            flash('Alguma coisa deu errado.')
 
    return render_template('retrieve.html', form=form)
 
if __name__ == "__main__":
    app.run()