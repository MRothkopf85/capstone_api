import os
from flask import Flask, jsonify
from flask_restful import Api, Resource, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://" + \
                                        os.environ['POST_USERNAME'] + ":" + \
                                        os.environ['POST_PASS'] + "@localhost:" + \
                                        os.environ['POST_PORT'] + "/" + \
                                        os.environ['POST_DB']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy()
ma = Marshmallow(app)


@app.before_first_request
def create_tables():
    db.create_all()

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
    def get(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        if new_recipe:
            return new_recipe.json()
        return {'message': 'A recipe with that name does not exist.'}, 404


    def post(self, name):
        if RecipeModel.find_by_name(name):
            return {"message": "A recipe with that name already exists"}, 400
        data = request.get_json()
        recipe_schema = RecipeSchema()
        new_recipe = RecipeModel(name=data["name"], ingredients=data["ingredients"], directions=data["directions"])
        db.session.add(new_recipe)
        db.session.commit()
        return recipe_schema.dump(new_recipe).data



    def delete(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        if new_recipe:
            db.session.delete(new_recipe)
            db.session.commit()
            return {'message': 'The recipe for {} has been deleted.'.format(name)}
        return {'message': 'Recipe not found'}, 404

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


api.add_resource(Recipe, '/recipe/<string:name>')
api.add_resource(RecipeList, '/recipes')


if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
