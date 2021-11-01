from flask import *
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = f"mongodb+srv://{os.environ['user']}:{os.environ['password']}@full-stack-web-developm.m7o9n.mongodb.net/space-invaders-top-scores?retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route("/get_scores", methods=["POST"])
def get_scores():
    if request.method == "POST":
        level = request.json["level"]
        amount = request.json["amount"]

        from_database = list(getattr(mongo.db, level).find())
        output = {k: v for d in from_database for k, v in d.items()}
        del output["_id"]
        output = dict(sorted(output.items(), key=lambda x: x[1]))
        print(output)
        user = {}
        for i in range(amount):
            try:
                user[list(output.keys())[i]] = list(output.values())[i]
            except IndexError:
                break
        return jsonify({"scores": user})


@app.route("/add_score", methods=["POST"])
def add_score():
    if request.method == "POST":
        level = request.json["level"]
        time = request.json["time"]
        name = request.json["name"]
        getattr(mongo.db, level).insert_one({name: time})
        return True


if __name__ == '__main__':
    app.run(debug=True)
