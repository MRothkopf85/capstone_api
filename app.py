import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.recipe import Recipe, RecipeList
from resources.user import UserRegister, UserLogin
from db import db


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


@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

api.add_resource(Recipe, '/recipe/<string:name>')
api.add_resource(RecipeList, '/recipes')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')


if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)
