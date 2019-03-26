import os
from flask import Flask, jsonify
from flask_restful import Api, Resource, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from passlib.context import CryptContext
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + \
                                        os.environ['POST_USERNAME'] + ":" + \
                                        os.environ['POST_PASS'] + "@localhost:" + \
                                        os.environ['POST_PORT'] + "/" + \
                                        os.environ['POST_DB']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.secret_key = os.environ['SECRET_KEY']
api = Api(app)
db = SQLAlchemy()
ma = Marshmallow(app)


@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)

# def authenticate(username, password):
#     user = UserModel.find_by_username(username)
#     if user and check_encrypted_password(password, user.password):
#         return user
#
# def identity(payload):
#     user_id = payload['identity']
#     return UserModel.find_by_id(user_id)

def encrypt_password(password):
    return pwd_context.encrypt(password)

def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


class RecipeModel(db.Model):
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    ingredients = db.Column(db.String(600))
    directions = db.Column(db.String(1000))

    def __init__(self, name, ingredients, directions):
        self.name = name
        self.ingredients = ingredients
        self.directions = directions

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'directions': self.directions
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class RecipeSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    ingredients = fields.Str()
    directions = fields.Str()

    class Meta:
        ordered=True

class Recipe(Resource):
    @jwt_required
    def get(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        if new_recipe:
            return new_recipe.json()
        return {'message': 'A recipe with that name does not exist.'}, 404

    @jwt_required
    def post(self, name):
        if RecipeModel.find_by_name(name):
            return {"message": "A recipe with that name already exists"}, 400
        data = request.get_json()
        recipe_schema = RecipeSchema()
        new_recipe = RecipeModel(name=data["name"], ingredients=data["ingredients"], directions=data["directions"])
        db.session.add(new_recipe)
        db.session.commit()
        return recipe_schema.dump(new_recipe).data

    @jwt_required
    def delete(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        if new_recipe:
            db.session.delete(new_recipe)
            db.session.commit()
            return {'message': 'The recipe for {} has been deleted.'.format(name)}
        return {'message': 'Recipe not found'}, 404

    @jwt_required
    def put(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        data = request.get_json()
        recipe_schema = RecipeSchema()
        if new_recipe:
            if data['ingredients'] != None:
                new_recipe.ingredients = data['ingredients']
            elif data['directions'] != None:
                new_recipe.directions = data['directions']
        else:
            new_recipe = RecipeModel(name=data["name"], ingredients=data["ingredients"], directions=data["directions"])

        db.session.add(new_recipe)
        db.session.commit()
        return recipe_schema.dump(new_recipe).data


class RecipeList(Resource):
    def get(self):
        return {'recipes': [x.json() for x in RecipeModel.find_all()]}


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200))
    password = db.Column(db.String(200))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def json(self):
        return {
            'id': self.id,
            'username': self.username
        }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class UserSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    username = fields.Str()

    class Meta:
        ordered=True

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        user_schema = UserSchema()
        password = encrypt_password(data["password"])
        new_user = UserModel(username=data["username"], password=password)
        if UserModel.find_by_username(new_user.username):
            return {"message": "That username is already in use"}
        else:
            new_user.save_to_db()
            return user_schema.dump(new_user).data

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        new_user = UserModel.find_by_username(data['username'])
        if new_user and check_encrypted_password(data['password'], new_user.password):
            access_token = create_access_token(identity=new_user.id, fresh=True)
            refresh_token = create_refresh_token(new_user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return  {'message': 'Invalid credentials'}, 401

api.add_resource(Recipe, '/recipe/<string:name>')
api.add_resource(RecipeList, '/recipes')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
