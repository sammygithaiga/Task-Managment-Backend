from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User

class SignupResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help="Username is required")
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        self.parser.add_argument('password_hash', type=str, required=True, help="Password_hash is required")
        self.parser.add_argument('role', type=str, required=True, help="Role is required")
        self.parser.add_argument('profile picture', type=str, required=True, help="Profile picture is required")
        super(SignupResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()

        # Check if username or email already exists
        username_exists = User.query.filter_by(username=data['username']).first()
        email_exists = User.query.filter_by(email=data['email']).first()
        if username_exists or email_exists:
            if username_exists:
                return {"message": "Username already taken", "status": "fail"}, 422
            else:
                return {"message": "Email address already taken", "status": "fail"}, 422

        # Generate password hash
        password_hash = generate_password_hash(data['password_hash']).decode('utf-8')

        # Create new user
        new_user = User(username=data['username'], email=data['email'], password_hash=password_hash)

        try:
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            return {"message": "Error creating user", "status": "fail", "error": str(e)}, 500

        # Return success message and user information
        return {"message": "User registered successfully", "status": "success", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}


class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password_hash', required=True, help="Password is required")

    def post(self):
        data = self.parser.parse_args()

        user = User.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password_hash, data['password']):
            user_dict = {"id": user.id, "role": user.role}
            additional_claims = {"role": user_dict['role']}
            access_token = create_access_token(identity=user_dict['id'], additional_claims=additional_claims)
            return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict}
        
        return {"message": "Invalid credentials", "status": "fail"}, 401