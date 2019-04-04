from security import encrypt_password, check_encrypted_password
from flask_restful import Resource, request
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import UserModel



class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        password = encrypt_password(data["password"])
        new_user = UserModel(username=data["username"], password=password)
        if UserModel.find_by_username(new_user.username):
            return {"message": "That username is already in use"}
        else:
            new_user.save_to_db()
            return new_user.json()

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