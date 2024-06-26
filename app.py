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

app = Flask(__name__)


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
    except:
        return "Not a valid tokopedia link.", 406
    
    return redirect(url_for('result', results=results))

@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return "404 Page Not Found", 404
