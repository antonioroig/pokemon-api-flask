from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from src.database import db
from src.models import User, Pokemon, Type, Favorite

api = Blueprint("api", __name__)


# ---------- Helpers ----------
def error(status: int, message: str):
    return jsonify({"error": message}), status


def get_json():
    if not request.is_json:
        return None
    return request.get_json(silent=True)


def user_to_dict(u: User):
    return {"id": u.id, "username": u.username}


def type_to_dict(t: Type):
    return {"id": t.id, "name": t.name}


def pokemon_to_dict(p: Pokemon):
    # relación en el modelo: p.poke_type
    return {"id": p.id, "name": p.name, "type_id": p.type_id, "type": p.poke_type.name if p.poke_type else None}


def favorite_to_dict(f: Favorite, expand=False):
    if not expand:
        return {"id": f.id, "user_id": f.user_id, "pokemon_id": f.pokemon_id}
    p = f.pokemon
    return {
        "id": f.id,
        "user_id": f.user_id,
        "pokemon": pokemon_to_dict(p) if p else None
    }


# ---------- Health ----------
@api.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


# ---------- Root ----------
@api.get("/")
def home():
    return jsonify({
        "name": "Pokemon API",
        "status": "ok",
        "health": "/health",
        "endpoints": [
            "/users",
            "/pokemons",
            "/types"
        ]
    }), 200


# ---------- Types ----------
@api.get("/types")
def list_types():
    types = Type.query.order_by(Type.id.asc()).all()
    return jsonify([type_to_dict(t) for t in types]), 200


@api.get("/types/<int:type_id>")
def get_type(type_id: int):
    t = Type.query.get(type_id)
    if not t:
        return error(404, "Type not found")
    return jsonify(type_to_dict(t)), 200


@api.post("/types")
def create_type():
    data = get_json()
    if not data:
        return error(400, "JSON body required")
    name = (data.get("name") or "").strip()
    if not name:
        return error(400, "Field 'name' is required")

    t = Type(name=name)
    db.session.add(t)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(409, "Type with that name already exists")

    return jsonify(type_to_dict(t)), 201


@api.put("/types/<int:type_id>")
@api.patch("/types/<int:type_id>")
def update_type(type_id: int):
    t = Type.query.get(type_id)
    if not t:
        return error(404, "Type not found")

    data = get_json()
    if not data:
        return error(400, "JSON body required")

    # PUT exige que venga name; PATCH lo hace opcional
    if request.method == "PUT" and "name" not in data:
        return error(400, "PUT requires field 'name'")

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return error(400, "Field 'name' cannot be empty")
        t.name = name

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(409, "Type with that name already exists")

    return jsonify(type_to_dict(t)), 200


@api.delete("/types/<int:type_id>")
def delete_type(type_id: int):
    t = Type.query.get(type_id)
    if not t:
        return error(404, "Type not found")

    db.session.delete(t)
    db.session.commit()
    return jsonify({"deleted": True, "id": type_id}), 200


# ---------- Pokemons ----------
@api.get("/pokemons")
def list_pokemons():
    pokemons = Pokemon.query.order_by(Pokemon.id.asc()).all()
    return jsonify([pokemon_to_dict(p) for p in pokemons]), 200


@api.get("/pokemons/<int:pokemon_id>")
def get_pokemon(pokemon_id: int):
    p = Pokemon.query.get(pokemon_id)
    if not p:
        return error(404, "Pokemon not found")
    return jsonify(pokemon_to_dict(p)), 200


@api.post("/pokemons")
def create_pokemon():
    data = get_json()
    if not data:
        return error(400, "JSON body required")

    name = (data.get("name") or "").strip()
    type_id = data.get("type_id")

    if not name:
        return error(400, "Field 'name' is required")
    if type_id is None:
        return error(400, "Field 'type_id' is required")

    t = Type.query.get(type_id)
    if not t:
        return error(400, "Invalid 'type_id' (type not found)")

    p = Pokemon(name=name, type_id=type_id)
    db.session.add(p)
    db.session.commit()
    return jsonify(pokemon_to_dict(p)), 201


@api.put("/pokemons/<int:pokemon_id>")
@api.patch("/pokemons/<int:pokemon_id>")
def update_pokemon(pokemon_id: int):
    p = Pokemon.query.get(pokemon_id)
    if not p:
        return error(404, "Pokemon not found")

    data = get_json()
    if not data:
        return error(400, "JSON body required")

    # PUT exige name y type_id; PATCH los hace opcionales
    if request.method == "PUT":
        if "name" not in data or "type_id" not in data:
            return error(400, "PUT requires fields 'name' and 'type_id'")

    if "name" in data:
        name = (data.get("name") or "").strip()
        if not name:
            return error(400, "Field 'name' cannot be empty")
        p.name = name

    if "type_id" in data:
        type_id = data.get("type_id")
        t = Type.query.get(type_id)
        if not t:
            return error(400, "Invalid 'type_id' (type not found)")
        p.type_id = type_id

    db.session.commit()
    return jsonify(pokemon_to_dict(p)), 200


@api.delete("/pokemons/<int:pokemon_id>")
def delete_pokemon(pokemon_id: int):
    p = Pokemon.query.get(pokemon_id)
    if not p:
        return error(404, "Pokemon not found")

    db.session.delete(p)
    db.session.commit()
    return jsonify({"deleted": True, "id": pokemon_id}), 200


# ---------- Users ----------
@api.get("/users")
def list_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([user_to_dict(u) for u in users]), 200


@api.get("/users/<int:user_id>")
def get_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")
    return jsonify(user_to_dict(u)), 200


@api.post("/users")
def create_user():
    data = get_json()
    if not data:
        return error(400, "JSON body required")

    username = (data.get("username") or "").strip()
    password = data.get("password")

    if not username:
        return error(400, "Field 'username' is required")
    if not password:
        return error(400, "Field 'password' is required")

    u = User(username=username)
    u.set_password(password)

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(409, "Username already exists")

    return jsonify(user_to_dict(u)), 201


@api.put("/users/<int:user_id>")
@api.patch("/users/<int:user_id>")
def update_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    data = get_json()
    if not data:
        return error(400, "JSON body required")

    # PUT exige username y password; PATCH opcional
    if request.method == "PUT":
        if "username" not in data or "password" not in data:
            return error(400, "PUT requires fields 'username' and 'password'")

    if "username" in data:
        username = (data.get("username") or "").strip()
        if not username:
            return error(400, "Field 'username' cannot be empty")
        u.username = username

    if "password" in data:
        password = data.get("password")
        if not password:
            return error(400, "Field 'password' cannot be empty")
        u.set_password(password)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(409, "Username already exists")

    return jsonify(user_to_dict(u)), 200


@api.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    db.session.delete(u)
    db.session.commit()
    return jsonify({"deleted": True, "id": user_id}), 200


# ---------- Favorites ----------
@api.get("/users/<int:user_id>/favorites")
def list_favorites(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    # ?expand=1 para devolver info del pokemon
    expand = request.args.get("expand") in ("1", "true", "yes")
    favs = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.id.asc()).all()
    return jsonify([favorite_to_dict(f, expand=expand) for f in favs]), 200


@api.post("/users/<int:user_id>/favorites")
def add_favorite(user_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    data = get_json()
    if not data:
        return error(400, "JSON body required")

    pokemon_id = data.get("pokemon_id")
    if pokemon_id is None:
        return error(400, "Field 'pokemon_id' is required")

    p = Pokemon.query.get(pokemon_id)
    if not p:
        return error(400, "Pokemon not found")

    # Evitar duplicados (mismo user + mismo pokemon)
    existing = Favorite.query.filter_by(user_id=user_id, pokemon_id=pokemon_id).first()
    if existing:
        return jsonify(favorite_to_dict(existing, expand=True)), 200

    f = Favorite(user_id=user_id, pokemon_id=pokemon_id)
    db.session.add(f)
    db.session.commit()
    return jsonify(favorite_to_dict(f, expand=True)), 201


@api.delete("/users/<int:user_id>/favorites/<int:favorite_id>")
def delete_favorite(user_id: int, favorite_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    f = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
    if not f:
        return error(404, "Favorite not found")

    db.session.delete(f)
    db.session.commit()
    return jsonify({"deleted": True, "id": favorite_id}), 200


# extra útil: borrar favorito por pokemon_id
@api.delete("/users/<int:user_id>/favorites/by-pokemon/<int:pokemon_id>")
def delete_favorite_by_pokemon(user_id: int, pokemon_id: int):
    u = User.query.get(user_id)
    if not u:
        return error(404, "User not found")

    f = Favorite.query.filter_by(user_id=user_id, pokemon_id=pokemon_id).first()
    if not f:
        return error(404, "Favorite not found")

    db.session.delete(f)
    db.session.commit()
    return jsonify({"deleted": True, "pokemon_id": pokemon_id}), 200
