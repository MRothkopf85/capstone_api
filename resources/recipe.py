from flask_restful import Resource, request
from models.recipe import RecipeModel, RecipeSchema
from flask_jwt_extended import jwt_required
from db import db



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