from typing import Tuple
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    request
)
from werkzeug.wrappers import Response

app = Flask(__name__)


@app.get('/')
def index() -> str:
    return render_template('index.html')

@app.get('/sentiment')
def sentiment() -> str:
    return render_template('sentiment.html')
@app.post('/submit')
def submit() -> Response:
    print(request.form['url'])
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return "404 Page Not Found", 404
