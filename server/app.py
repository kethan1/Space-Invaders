import os
import urllib.parse

from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo
from dotenv import load_dotenv

if "DYNO" not in os.environ:
    load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb+srv://{os.environ['user']}:{os.environ['password']}@full-stack-web-developm.m7o9n.mongodb.net/space-invaders-top-scores?retryWrites=true&w=majority"
mongo = PyMongo(app)


# @app.before_request
# def before_request():
#     if 'DYNO' in os.environ and request.url.startswith('http://'):
#         url = request.url.replace('http://', 'https://', 1)
#         return redirect(urllib.parse.quote(url), code=301)


@app.route("/get_scores", methods=["POST"])
def get_scores():
    level = request.json["level"]
    amount = request.json["amount"]

    from_database = list(getattr(mongo.db, level).find())
    output = [[k, v] for d in from_database for k, v in d.items() if k != "_id"]
    output = list(sorted(output, key=lambda x: x[1]))
    return jsonify({"scores": output[:amount]})


@app.route("/add_score", methods=["POST"])
def add_score():
    level = request.json["level"]
    time = request.json["time"]
    name = request.json["name"]
    getattr(mongo.db, level).insert_one({name: time})
    return jsonify(True)


@app.route("/signup", methods=["POST"])
def sign_up():
    username = request.json["username"]
    password = request.json["password"]
    if mongo.db.users.find_one({"username": username}) is None:
        mongo.db.users.insert_one({"username": username, "password": password})
    else:
        return jsonify({"already_exists": True})
    return jsonify({"already_exists": False})


@app.route("/login", methods=["POST"])
def login():
    username = request.json["username"]
    password = request.json["password"]
    found = mongo.db.users.find_one({"username": username, "password": password})
    if found is None:
        return jsonify({"incorrect_info": True})
    return jsonify({"incorrect_info": False})


if __name__ == '__main__':
    app.run(debug=True)
