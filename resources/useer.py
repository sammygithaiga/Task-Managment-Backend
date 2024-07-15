from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash
from models import db, User
from functools import wraps

class SignupResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help="Username is required")
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        self.parser.add_argument('password_hash', type=str, required=True, help="Password_hash is required")
        self.parser.add_argument('role', type=str, required=True, help="Role is required")
        self.parser.add_argument('profile_picture', type=str, required=True, help="Profile picture is required")
        super(SignupResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()

        username_exists = User.query.filter_by(username=data['username']).first()
        email_exists = User.query.filter_by(email=data['email']).first()
        if username_exists or email_exists:
            if username_exists:
                return {"message": "Username already taken", "status": "fail"}, 422
            else:
                return {"message": "Email address already taken", "status": "fail"}, 422

        password_hash = generate_password_hash(data['password_hash']).decode('utf-8')

        new_user = User(username=data['username'], email=data['email'], password_hash=password_hash, role=data['role'], profile_picture=data['profile_picture'])

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return {"message": "Error creating user", "status": "fail", "error": str(e)}, 500

        return {"message": "User registered successfully", "status": "success", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}


class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password', required=True, help="Password is required")
    parser.add_argument('role', required=True, help="Role is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password_hash, data['password']):
            if data['role'] == user.role:
                user_dict = {"id": user.id, "role": user.role}
                access_token = create_access_token(identity=user_dict)
                if user.role == 'admin':
                    return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict, "redirect": "/admin"}
                else:
                    return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict, "redirect": "/user"}
            else:
                return {"message": "Invalid role", "status": "fail"}, 401
        else:
            return {"message": "Invalid credentials", "status": "fail"}, 401


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role != 'admin':
            return {"message": "Only admins are allowed to access this resource"}, 403
        return func(*args, **kwargs)
    return decorated_function


class ProtectedResource(Resource):
    @jwt_required
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role == 'admin':
            return {"message": "Admin view"}
        else:
            return {"message": "User view"}


class AdminResource(Resource):
    @jwt_required
    @admin_required
    def get(self):
        return {"message": "Admin resource"}