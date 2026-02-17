# routes.py - Definición de los endpoints de la API
from flask import jsonify, request
from src.app import app, db
from src.models import User, Pokemon, Type, Favorite

# ------------------- Usuarios -------------------
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})


# ------------------- Pokémon -------------------
@app.route('/pokemons', methods=['GET'])
def get_pokemons():
    pokemons = Pokemon.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'type': p.type.name} for p in pokemons])

@app.route('/pokemons', methods=['POST'])
def create_pokemon():
    data = request.json
    new_pokemon = Pokemon(name=data['name'], type_id=data['type_id'])
    db.session.add(new_pokemon)
    db.session.commit()
    return jsonify({'message': 'Pokemon created successfully'}), 201

@app.route('/pokemons/<int:pokemon_id>', methods=['DELETE'])
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.get_or_404(pokemon_id)
    db.session.delete(pokemon)
    db.session.commit()
    return jsonify({'message': 'Pokemon deleted'})


# ------------------- Tipos -------------------
@app.route('/types', methods=['GET'])
def get_types():
    types = Type.query.all()
    return jsonify([{'id': t.id, 'name': t.name} for t in types])

@app.route('/types', methods=['POST'])
def create_type():
    data = request.json
    new_type = Type(name=data['name'])
    db.session.add(new_type)
    db.session.commit()
    return jsonify({'message': 'Type created successfully'}), 201

@app.route('/types/<int:type_id>', methods=['DELETE'])
def delete_type(type_id):
    type_obj = Type.query.get_or_404(type_id)
    db.session.delete(type_obj)
    db.session.commit()
    return jsonify({'message': 'Type deleted'})


# ------------------- Favoritos -------------------
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([{'pokemon_id': f.pokemon_id} for f in favorites])

@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorite(user_id):
    data = request.json
    new_favorite = Favorite(user_id=user_id, pokemon_id=data.get('pokemon_id'))
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite added successfully'}), 201

@app.route('/users/<int:user_id>/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(user_id, favorite_id):
    favorite = Favorite.query.get_or_404(favorite_id)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'message': 'Favorite removed'})