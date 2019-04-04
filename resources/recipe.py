from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request
from models.recipe import RecipeModel



class RecipeResource(Resource):
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
        new_recipe = RecipeModel(name=data["name"], ingredients=data["ingredients"], directions=data["directions"])
        try:
            new_recipe.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}
        return new_recipe.json()

    @jwt_required
    def delete(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        if new_recipe:
            new_recipe.delete_from_db()
            return {'message': 'The recipe for {} has been deleted.'.format(name)}
        return {'message': 'Recipe not found'}, 404

    @jwt_required
    def put(self, name):
        new_recipe = RecipeModel.find_by_name(name)
        data = request.get_json()
        if new_recipe:
            if data['ingredients']:
                new_recipe.ingredients = data['ingredients']
            elif data['directions']:
                new_recipe.directions = data['directions']
        else:
            new_recipe = RecipeModel(name=data["name"], ingredients=data["ingredients"], directions=data["directions"])

        new_recipe.save_to_db()
        return new_recipe.json()


class RecipeList(Resource):
    def get(self):
        return {'recipes': [x.json() for x in RecipeModel.find_all()]}