"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    users = User.query.all()
    all_users = list(map(lambda u: u.serialize(),users))
    if users is None:
        return "User not found", 400
    
    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def handle_user_by_id(user_id):

    user = User.query.get(user_id)
    if user is None:
        return "User not found", 400
    response_body = user.serialize()
    
    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def handle_all_people():

    people_result = People.query.all()
    all_people = list(map(lambda u: u.serialize(),people_result))

    return jsonify(all_people), 200

@app.route('/people/<int:id>', methods=['GET'])
def handle_people_by_id(id):

    person = People.query.get(id)
    if person is None:
        return "Person not found", 400
    response_body = person.serialize()
    
    return jsonify(response_body), 200

@app.route('/planet', methods=['GET'])
def handle_all_planets():

    planet_result = Planet.query.all()
    all_planets = list(map(lambda u: u.serialize(),planet_result))

    return jsonify(all_planets), 200


@app.route('/planet/<int:planet_id>', methods=['GET'])
def handle_planet_by_id(planet_id):

    planet = Planet.query.get(planet_id)
    if planet is None:
        return "Planet not found", 400
    response_body = planet.serialize()    

    return jsonify(response_body), 200


@app.route('/<int:user_id>/favorites', methods=['GET'])
def handle_favs_by_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return "User not found", 400
    
    fav_planets = [{"id": planet.id, "name":planet.name} for planet in user.favorite_planets]
    fav_people = [{"id": people.id, "name": people.name} for people in user.favorite_people]

    return jsonify({"favorite Planets": fav_planets, "favorite People": fav_people}), 200

@app.route('/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_fav_by_planet_id(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    if planet in user.favorite_planets:
        return jsonify({"message": "Planet already added as favorite"}), 400
    
    user.favorite_planets.append(planet)
    db.session.commit()
    
    return jsonify({"message": "Planet added successfully"}), 201

@app.route('/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def add_fav_by_people_id(user_id, people_id):
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    if person in user.favorite_people:
        return jsonify({"message": "Planet already added as favorite"}), 400
    
    user.favorite_people.append(person)
    db.session.commit()
    
    return jsonify({"message": "Person added successfully"}), 201

@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return "You need to fill the fields to create an user", 400
    
    new_user = User(is_active=data['is_active'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message":"User created", "data":data}), 201

@app.route('/planet', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data:
        return "You need to fill the name of the planet", 400
    
    new_planet = Planet(name=data['name'])
    db.session.add(new_planet)
    db.session.commit()
    
    return jsonify({"message":"Planet created", "data":data}), 201

@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if not data:
        return "You need to fill the name of the person", 400
    
    new_person = People(name=data['name'])
    db.session.add(new_person)
    db.session.commit()
    
    return jsonify({"message":"Person created", "data":data}), 201

@app.route('/<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_by_planet_id(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not planet:
        return jsonify({"error": "Planet not found"}), 404
    
    if not planet in user.favorite_planets:
        return jsonify({"error": "Planet not present on favorite planets list"}), 404
    
    user.favorite_people.remove(planet)
    db.session.commit()
    
    return jsonify({"message": "Planet deleted successfully"}), 201

@app.route('/<int:user_id>/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_by_people_id(user_id, people_id):
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if not person:
        return jsonify({"error": "Person not found"}), 404
    
    if not person in user.favorite_people:
        return jsonify({"error": "Person not present on favorite people list"}), 404
    
    user.favorite_people.remove(person)
    db.session.commit()
    
    return jsonify({"message": "Person deleted successfully"}), 201


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
