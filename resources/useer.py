from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash
from models import db, User
from functools import wraps
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SignupResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help="Username is required")
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        self.parser.add_argument('password', type=str, required=True, help="Password is required")
        self.parser.add_argument('role', type=str, required=True, help="Role is required")
        self.parser.add_argument('phone', type=str, required=True, help="Phone is required")
        super(SignupResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        try:
            username_exists = User.query.filter_by(username=data['username']).first()
            email_exists = User.query.filter_by(email=data['email']).first()
            if username_exists or email_exists:
                if username_exists:
                    return {"message": "Username already taken", "status": "fail"}, 422
                else:
                    return {"message": "Email address already taken", "status": "fail"}, 422

            password_hash = generate_password_hash(data['password']).decode('utf-8')

            new_user = User(username=data['username'], email=data['email'], password_hash=password_hash, role=data['role'])

            db.session.add(new_user)
            db.session.commit()
            return {"message": "User registered successfully", "status": "success", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            return {"message": "Error creating user", "status": "fail", "error": str(e)}, 500

class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password', required=True, help="Password is required")
    parser.add_argument('role', required=True, help="Role is required")

    def post(self):
        data = self.parser.parse_args()
        try:
            user = User.query.filter_by(email=data['email']).first()

            if user and check_password_hash(user.password_hash, data['password']):
                if data['role'] == user.role:
                    user_dict = {"id": user.id, "role": user.role}
                    access_token = create_access_token(identity=user_dict)
                    logger.debug(f"Generated Token: {access_token}")
                    if user.role == 'admin':
                        return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict, "redirect": "/admin"}
                    else:
                        return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict, "redirect": "/user"}
                else:
                    return {"message": "Invalid role", "status": "fail"}, 401
            else:
                return {"message": "Invalid credentials", "status": "fail"}, 401
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return {"message": "Error during login", "status": "fail", "error": str(e)}, 500

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if user.role != 'admin':
                return {"message": "Only admins are allowed to access this resource"}, 403
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in admin_required: {e}")
            return {"message": "Error during authorization", "status": "fail", "error": str(e)}, 500
    return decorated_function

class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            logger.debug(f"Decoded Token Identity: {user_id}")
            user = User.query.get(user_id)
            if user.role == 'admin':
                return {"message": "Admin view"}
            else:
                return {"message": "User view"}
        except Exception as e:
            logger.error(f"Error in ProtectedResource: {e}")
            return {"message": "Error retrieving resource", "status": "fail", "error": str(e)}, 500

class AdminResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        try:
            return {"message": "Admin resource"}
        except Exception as e:
            logger.error(f"Error in AdminResource: {e}")
            return {"message": "Error retrieving admin resource", "status": "fail", "error": str(e)}, 500
