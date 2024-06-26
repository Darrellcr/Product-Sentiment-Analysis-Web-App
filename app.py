from typing import Tuple
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request
)
from werkzeug.wrappers import Response
from functions.scrape_tokped import scrape_tokopedia
from functions.extract_aspect import get_aspect
from functions.get_sentiment import get_sentiment
import json
import pandas as pd
import re

app = Flask(__name__)
results = []

@app.get('/')
def index() -> str:
    return render_template('index.html')

@app.get('/sentiment')
def sentiment() -> str:
    return render_template('sentiment.html')

@app.get('/tutorial')
def tutorial() -> str:
    return render_template('tutorial.html')

@app.get('/credit')
def credit() -> str:
    return render_template('credit.html') 

@app.get('/about')
def about() -> str:
    return render_template('about.html')

@app.get('/result')
def result() -> str:
    return render_template('result.html')

@app.post('/submit')
def submit() -> Response:
    url = request.form['url']

    try:
        product_name, img_src, reviews = scrape_tokopedia(url)
        results = get_aspect(reviews)
        results = get_sentiment(results)
    except Exception as e:
        return e, 406
        # return "Not a valid tokopedia link.", 406

    data = pd.DataFrame(results)
    data = data.replace(r'\n',' ', regex=True)
    data = data.replace(r'"','', regex=True)
    count = len(results)
    results = data
    print(results)
    data = data.drop(['review'], axis=1, inplace=False)
    barang = data[data['aspect'] == 'barang'].groupby('sentiment').count().to_json(force_ascii=False)
    pengiriman =  data[data['aspect'] == 'pengiriman'].groupby('sentiment').count().to_json(force_ascii=False)
    pelayanan = data[data['aspect'] == 'pelayanan'].groupby('sentiment').count().to_json(force_ascii=False)

    # results = json.dumps(results)
    return render_template('sentiment.html', name=product_name, img=img_src, count=count, barang=barang, pengiriman=pengiriman, pelayanan=pelayanan, results=results.to_json(orient='records', force_ascii=False))

@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return "404 Page Not Found", 404
