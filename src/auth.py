from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flasgger import swag_from

from src.database import Level, db,LevelSchema, User, UserSchema


auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

user_schema = UserSchema()
users_schema = UserSchema(many=True)
level_schema = LevelSchema()
levels_schema = LevelSchema(many=True)


@auth.get('/users')
@jwt_required()
@swag_from('./docs/auth/users.yaml')
def get_users():
    id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=id).first()

    if logged_in_user.level_id != 1:
        return jsonify(msg="unauthorized"), HTTP_401_UNAUTHORIZED
    
    users = User.query.all()


    return jsonify(users_schema.dump(users)), 200


@auth.get('/user')
@jwt_required()
@swag_from('./docs/auth/user.yaml')
def get():
    id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=id).first()

    return jsonify(user=user_schema.dump(logged_in_user)), HTTP_200_OK


@auth.put('/edit-user')
@jwt_required()
@swag_from("./docs/auth/edit-user.yaml")
def edit():
    id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=id).first()

    if logged_in_user.level_id != 1:
        return jsonify(msg="forbidden"), HTTP_401_UNAUTHORIZED
    
    id = request.json.get('id', '')
    name = request.json.get('name', '')
    lvl = request.json.get('level', '')

    if not id or not name or not lvl:
        return jsonify(msg="missing data"), HTTP_400_BAD_REQUEST
    
    user = User.query.get(id)
    if not user:
        return jsonify(msg="user not found"), HTTP_404_NOT_FOUND
    
    level = Level.query.filter_by(name=lvl).first()

    if not level:
        return jsonify(msg="level not found"), HTTP_404_NOT_FOUND

    user.name = name
    user.level_id = level.id
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "edit successful",
        "user": user_schema.dump(user)
    }), 200


@auth.post('/add-user')
@jwt_required()
@swag_from("./docs/auth/add-user.yaml")
def add_user():
    id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=id).first()

    if logged_in_user.level_id != 1:
        return jsonify(msg="unauthorized"), HTTP_401_UNAUTHORIZED

    name = request.json.get('name', '')
    username = request.json.get('username', '')
    lvl = request.json.get('level', '')
    passw = request.json.get('password', '')

    if not name or not username or not lvl or not passw:
        return jsonify(msg="Missing Data!"), HTTP_400_BAD_REQUEST
    
    level = Level.query.filter_by(name=lvl).first()

    if not level:
        return jsonify(msg=f"Level '{lvl}' does not exist!"), HTTP_400_BAD_REQUEST
    

    user = User.query.filter_by(username=username).first()

    if user:
        return jsonify(msg=f"Username {username} taken!"), HTTP_409_CONFLICT
    

    if len(passw) < 8:
        return jsonify(msg="Password is too short"), HTTP_400_BAD_REQUEST
    
    passw_hash = generate_password_hash(passw)
    
    user = User(name=name, username=username, level=level, passw_hash=passw_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "msg": "user created",
        "user": user_schema.dump(user)
    }), HTTP_201_CREATED


@auth.delete('/del-user/<id>')
@jwt_required()
@swag_from("./docs/auth/del-user.yaml")
def del_user(id):
    logged_id = get_jwt_identity()
    logged_in_user = User.query.filter_by(id=logged_id).first()

    if logged_in_user.level_id != 1:
        return jsonify(msg="unauthorized"), HTTP_401_UNAUTHORIZED
    
    user = User.query.get(id)
    if not user:
        return jsonify(msg="user does not exist"), HTTP_404_NOT_FOUND
    
    if logged_in_user.username == user.username:
        return jsonify(msg="cannot delete self"), HTTP_403_FORBIDDEN 
    
    db.session.delete(user)
    db.session.commit()

    return jsonify(msg="user deleted successfully"), HTTP_200_OK


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    username = request.json.get('username', '')
    passw = request.json.get('password', '')

    if not username or not passw:
        return jsonify(msg="missing parameter"), HTTP_400_BAD_REQUEST
    
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify(msg=f"user '{username}' does not exist"), HTTP_404_NOT_FOUND
    
    passw_check = check_password_hash(user.passw_hash, passw)

    if not passw_check:
        return jsonify(msg="wrong password"), HTTP_401_UNAUTHORIZED
    
    return jsonify({
        "access": create_access_token(user.id),
        "refresh": create_refresh_token(user.id),
        "user": user_schema.dump(user)
    })


@auth.get('/refresh')
@jwt_required(refresh=True)
@swag_from('./docs/auth/refresh.yaml')
def handle_refresh():
    id = get_jwt_identity()

    user = User.query.get(id)

    if not user:
        return jsonify(msg="user does not exist"), HTTP_404_NOT_FOUND
    
    return jsonify({
        "access": create_access_token(id),
        "refresh": create_refresh_token(id),
        "user": user_schema.dump(user)
    }), HTTP_200_OK
