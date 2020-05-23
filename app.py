from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


app = Flask(__name__)


mongo = PyMongo(app, uri="mongodb://localhost:27017/mars")


@app.route('/')
def home():
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)


@app.route('/scrape')
def scrape():
    #mars = mongo.db.collection
    data = scrape_mars.scrape_info()
    mongo.db.mars.update(
        {},
        data,
        upsert=True
    )
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)