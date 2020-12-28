from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import json
from bson.json_util import dumps, ObjectId
import re
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

load_dotenv()
DB_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DBNAME")

app.config['MONGO_DBNAME'] = DB_NAME
app.config['MONGO_URI'] = DB_URI

client = MongoClient(DB_URI)
db = client[DB_NAME]
cheeses_collection = db['cheeses']


def parse_json(data):
    return json.loads(dumps(data))


@app.route('/cheeses', methods=['GET'])
def get_all_items():
    collection = cheeses_collection.find()
    response = []
    for item in collection:
        item['_id'] = parse_json(item['_id'])
        response.append(item)
    return jsonify(response), 200


@app.route('/cheeses', methods=['POST'])
def add_item():
    request_data = request.json
    cheeses_collection.insert_one(request_data)
    return dumps(request_data), 201


@app.route("/cheeses/<item_id>", methods=['GET'])
def get_one_item(item_id):
    item = cheeses_collection.find_one({"_id": ObjectId(item_id)})
    item['_id'] = parse_json(item['_id'])
    return jsonify(item), 200


@app.route("/cheeses/<item_id>", methods=['PUT'])
def update_item(item_id):
    if cheeses_collection.find_one({'_id': ObjectId(item_id)}) is None:
        return "No item with this id", 204
    request_data = request.json
    title = request_data['title']
    img = request_data['img']
    price = request_data['price']
    cheeses_collection.update_one({'_id': ObjectId(item_id)}, {'$set': {'price': price, 'title': title, 'img': img}})
    return jsonify(request_data), 200


@app.route("/cheeses/<item_id>", methods=['DELETE'])
def delete_item(item_id):
    if cheeses_collection.find_one({'_id': ObjectId(item_id)}) is None:
        return "No item with this id", 204
    cheeses_collection.delete_one({'_id': ObjectId(item_id)})
    return "Deleted", 202


@app.route('/cheeses/filter/<product_type>', methods=['GET'])
def get_items_by_type(product_type):
    collection = cheeses_collection.find({'title': re.compile(product_type, re.IGNORECASE)})
    response = []
    for item in collection:
        item['_id'] = parse_json(item['_id'])
        response.append(item)

    return jsonify(response), 200


@app.route('/cheeses/filter/<int:price>', methods=['GET'])
def get_items_with_price_lower_than(price):
    collection = cheeses_collection.find({"price": {"$lt": price}})
    response = []
    for item in collection:
        item['_id'] = parse_json(item['_id'])
        response.append(item)

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)
