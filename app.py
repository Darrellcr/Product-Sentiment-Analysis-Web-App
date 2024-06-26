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

    # reviews = [{"review":"kwalitas original, di pakai nya nyaman di kaki... mantap... \ud83d\udc4d"},{"review":"ukuran sesuai, barang sesuai deskripsi, idk bedain ori ngga but from what i see.. definitely original.."},{"review":"barangnya bagus"},{"review":"ok sesuai pesanan"},{"review":"Sepatu yang jarang ada, sekilas kualitasnya bagus. Semoga sepatunya bisa awet."},{"review":"sesuai deskripsi, packing rapih & aman, pengiriman on time,","aspect":"pengiriman","sentiment":"Positive"},{"review":"sesuai deskripsi, packing rapih & aman, pengiriman on time,"},{"review":"model dan kualitas dijamin ori. semoga awet."},{"review":"Sesuai pesanan, desain bgs. semoga awet\ud83d\ude01."},{"review":"original. Reebok. harga murah. terjangkau. pengiriman cepat. ukuran sesuai. dah beli ketiga di sini. Mantap pokoknya","aspect":"pengiriman","sentiment":"Positive"},{"review":"original. Reebok. harga murah. terjangkau. pengiriman cepat. ukuran sesuai. dah beli ketiga di sini. Mantap pokoknya"},{"review":"model keren...sesuai produknya...packing double dus"},{"review":"Pengirimannya cepat, packing sangat rapih, barang sesuai orderan. Mantapp","aspect":"pengiriman","sentiment":"Positive"},{"review":"Pengirimannya cepat, packing sangat rapih, barang sesuai orderan. Mantapp"},{"review":"Sepatunya keren banget, mantap"},{"review":"di deskripsi tertulis \"Order yang masuk diatas jam close order kami, akan di proses di hari selanjut nya\". tapi saya order di bawah jam close tetep dikirim nya h+... ","aspect":"pelayanan","sentiment":"Negative"},{"review":"di deskripsi tertulis \"Order yang masuk diatas jam close order kami, akan di proses di hari selanjut nya\". tapi saya order di bawah jam close tetep dikirim nya h+... ","aspect":"barang","sentiment":"Negative"},{"review":"Mantap modelnya \ud83d\udc5f Desainnya keren \ud83d\udc4d Packaging aman \ud83d\ude4f","aspect":"pengiriman","sentiment":"Positive"},{"review":"Mantap modelnya \ud83d\udc5f Desainnya keren \ud83d\udc4d Packaging aman \ud83d\ude4f"},{"review":"Sepatunya nyaman Desainnya keren \ud83d\udc4d Mantap modelnya \ud83d\udc5f Bahannya berkualitas Ukuran sesuai Proses pesanan cepat Packaging aman \ud83d\ude4f Respon penjualnya top Packaging rapi Penj... ","aspect":"pelayanan","sentiment":"Positive"},{"review":"Sepatunya nyaman Desainnya keren \ud83d\udc4d Mantap modelnya \ud83d\udc5f Bahannya berkualitas Ukuran sesuai Proses pesanan cepat Packaging aman \ud83d\ude4f Respon penjualnya top Packaging rapi Penj... ","aspect":"pengiriman","sentiment":"Positive"},{"review":"Sepatunya nyaman Desainnya keren \ud83d\udc4d Mantap modelnya \ud83d\udc5f Bahannya berkualitas Ukuran sesuai Proses pesanan cepat Packaging aman \ud83d\ude4f Respon penjualnya top Packaging rapi Penj... "},{"review":"Pembelian kesekian-sekian,...respon penjual selalu yg terbaik, kualitas sepatu gak usa diragukan. Terima kasih.","aspect":"pelayanan","sentiment":"Positive"},{"review":"Pembelian kesekian-sekian,...respon penjual selalu yg terbaik, kualitas sepatu gak usa diragukan. Terima kasih."}]
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
    results = data
    print(results)
    data = data.drop(['review'], axis=1, inplace=False)
    barang = data[data['aspect'] == 'barang'].groupby('sentiment').count().to_json(force_ascii=False)
    pengiriman =  data[data['aspect'] == 'pengiriman'].groupby('sentiment').count().to_json(force_ascii=False)
    pelayanan = data[data['aspect'] == 'pelayanan'].groupby('sentiment').count().to_json(force_ascii=False)

    # results = json.dumps(results)
    return render_template('sentiment.html', barang=barang, pengiriman=pengiriman, pelayanan=pelayanan, results=results.to_json(orient='records', force_ascii=False))

@app.errorhandler(404)
def page_not_found(e) -> Tuple[str, int]:
    return "404 Page Not Found", 404
