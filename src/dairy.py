from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from

from src.database import BreedSchema, GenderSchema, db, Breed, Cow, CowSchema, Gender
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

dairy = Blueprint('dairy', __name__, url_prefix='/api/v1/dairy')


cow_schema = CowSchema()
cows_schema = CowSchema(many=True)
breed_schema = BreedSchema()
breeds_schema = BreedSchema(many=True)
gender_schema = GenderSchema()
genders_schema = GenderSchema(many=True)


@dairy.get('/cows')
@jwt_required()
@swag_from("./docs/dairy/cows.yaml")
def get_cows():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    cows = Cow.query.paginate(page=page, per_page=per_page)

    meta = {
        "page": cows.page,
        "pages": cows.pages,
        "total_count": cows.total,
        "prev_page": cows.prev_num,
        "next_page": cows.next_num,
        "has_next": cows.has_next,
        "has_prev": cows.has_prev

    }
    
    return jsonify({
        "cows": cows_schema.dump(cows.items),
        "meta": meta
    }), HTTP_200_OK


@dairy.get('/cow/<id>')
@jwt_required()
@swag_from("./docs/dairy/cow.yaml")
def get_cow(id):
    cow = Cow.query.get(id)

    if not cow:
        return jsonify(msg="cow not found"), HTTP_404_NOT_FOUND
    
    return jsonify(cow_schema.dump(cow)), HTTP_200_OK


@dairy.post('/add-cow')
@jwt_required()
@swag_from('./docs/dairy/add-cow.yaml')
def add_cow():
    name = request.json.get('name', '')
    dob = request.json.get('dob', '')
    breed = request.json.get('breed', '')
    gender = request.json.get('gender', '')

    if not name or not dob or not breed or not gender:
        return jsonify(msg="missing parameter"), HTTP_400_BAD_REQUEST
    
    bred = Breed.query.filter_by(name=breed).first()

    if not bred:
        return jsonify(msg="breed not found"), HTTP_404_NOT_FOUND
    
    gend = Gender.query.filter_by(name=gender).first()

    if not gend:
        return jsonify(msg="gender not found"), HTTP_404_NOT_FOUND

    srch_cow = Cow.query.filter_by(name=name).first()

    if srch_cow:
        return jsonify(msg=f"a cow with the name '{name}' exists"), HTTP_409_CONFLICT 
    
    dob = check_date(dob)

    if not dob:
        return jsonify(msg="wrong date of birth format"), HTTP_400_BAD_REQUEST
    
    cow = Cow(name=name, dob=dob, breed_id=bred.id, gender_id=gend.id)

    db.session.add(cow)
    db.session.commit()

    return jsonify({
        "msg": "cow added",
        "cow": cow_schema.dump(cow)
    }), HTTP_201_CREATED


@dairy.put('/edit-cow')
@jwt_required()
@swag_from('./docs/dairy/edit-cow.yaml')
def edit_cow():
    name = request.json.get('name', '')
    milk = request.json.get('milk', '')

    if not name or not milk:
        return jsonify(msg="missing parameter(s)"), HTTP_400_BAD_REQUEST
    
    cow = Cow.query.filter_by(name=name).first()

    if not cow:
        return jsonify(msg=f"cow {name} not found"), HTTP_404_NOT_FOUND
    
    cow.milk = milk
    cow.updated_at = datetime.utcnow()

    db.session.add(cow)
    db.session.commit()

    return jsonify({
        "msg": "successfull update",
        "cow": cow_schema.dump(cow)
    }), HTTP_200_OK


@dairy.delete('/del-cow/<id>')
@jwt_required()
@swag_from('./docs/dairy/del-cow.yaml')
def del_cow(id):
    cow = Cow.query.get(id)

    if not cow:
        return jsonify(msg="cow not found"), HTTP_404_NOT_FOUND

    db.session.delete(cow)
    db.session.commit()

    return jsonify(msg="successful delete"), HTTP_200_OK


@dairy.get('/breeds')
@jwt_required()
@swag_from("./docs/dairy/breeds.yaml")
def get_breeds():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    breeds = Breed.query.paginate(page=page, per_page=per_page)

    meta = {
        "page": breeds.page,
        "pages": breeds.pages,
        "total_count": breeds.total,
        "prev_page": breeds.prev_num,
        "next_page": breeds.next_num,
        "has_next": breeds.has_next,
        "has_prev": breeds.has_prev

    }

    return jsonify({
        "breeds": breeds_schema.dump(breeds.items),
        "meta": meta
    }), HTTP_200_OK


@dairy.get('/breed/<breed>')
@jwt_required()
@swag_from('./docs/dairy/breed.yaml')
def get_breed(breed):
    brd = Breed.query.filter_by(name=breed).first()

    if not brd:
        return jsonify(msg=f"breed '{breed}' not found"), HTTP_404_NOT_FOUND
    

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    cows = Cow.query.filter_by(breed_id=brd.id).paginate(page=page, per_page=per_page)

    meta = {
        "page": cows.page,
        "pages": cows.pages,
        "total_count": cows.total,
        "prev_page": cows.prev_num,
        "next_page": cows.next_num,
        "has_next": cows.has_next,
        "has_prev": cows.has_prev

    }

    return jsonify({
        "breed": breed,
        "cows": cows_schema.dump(cows.items),
        "meta": meta
    }), HTTP_200_OK


@dairy.get('/gender/<gender>')
@jwt_required()
@swag_from('./docs/dairy/gender.yaml')
def get_gender(gender):

    gnda = Gender.query.filter_by(name=gender).first()
    
    if not gnda:
        return jsonify(msg=f"'{gender}' not found"), HTTP_404_NOT_FOUND
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    cows = Cow.query.filter_by(gender_id=gnda.id).paginate(page=page, per_page=per_page)

    meta = {
        "page": cows.page,
        "pages": cows.pages,
        "total_count": cows.total,
        "prev_page": cows.prev_num,
        "next_page": cows.next_num,
        "has_next": cows.has_next,
        "has_prev": cows.has_prev

    }


    return jsonify({
        "gender": gender,
        "cows": cows_schema.dump(cows.items),
        "meta": meta
    }), HTTP_200_OK


@dairy.get('/cow-gend/<breed>/<gender>')
@jwt_required()
@swag_from('./docs/dairy/breed-gend.yaml')
def get_breed_gender(breed, gender):
    gnda = Gender.query.filter_by(name=gender).first()
    
    if not gnda:
        return jsonify(msg=f"'{gender}' not found"), HTTP_404_NOT_FOUND
    
    brd = Breed.query.filter_by(name=breed).first()

    if not brd:
        return jsonify(msg=f"breed '{breed}' not found"), HTTP_404_NOT_FOUND
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    cows = Cow.query.filter_by(gender_id=gnda.id, breed_id=brd.id).paginate(page=page, per_page=per_page)

    meta = {
        "page": cows.page,
        "pages": cows.pages,
        "total_count": cows.total,
        "prev_page": cows.prev_num,
        "next_page": cows.next_num,
        "has_next": cows.has_next,
        "has_prev": cows.has_prev

    }

    return jsonify({
        "cows" :cows_schema.dump(cows.items),
        "meta": meta
    }), HTTP_200_OK



#Helper functions
def check_date(dob):
    dob_splt = dob.split('-')
    
    if len(dob_splt) != 3:
        return None
    
    try:
        dob_splt = [int(d) for d in dob_splt]

        return datetime(dob_splt[0], dob_splt[1], dob_splt[2])
    
    except:
        return None