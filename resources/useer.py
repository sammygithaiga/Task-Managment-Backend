from flask_restful import Resource, reqparse
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db, User

class SignupResource(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('username', required=True, help="Username is required")
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password_hash', required=True, help="Password is required")

    def post(self):
       
        data = self.parser.parse_args()

        
        hashed_password = generate_password_hash(data['password']).decode('utf-8')

        
        if User.query.filter_by(email=data['email']).first():
            return {"message": "Email address already taken", "status": "fail"}, 422

        
        user = User(username=data['username'], email=data['email'], password_hash=hashed_password)

       
        db.session.add(user)
        db.session.commit()

        return {"message": "User registered successfully", "status": "success", "user": user.to_dict()}


class LoginResource(Resource):
    
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password_hash', required=True, help="Password is required")

    def post(self):
      
        data = self.parser.parse_args()

        
        user = User.query.filter_by(email=data['email']).first()

        
        if user and check_password_hash(user.password_hash, data['password']):
            user_dict = user.to_dict()
            additional_claims = {"role": user_dict['role']}
            access_token = create_access_token(identity=user_dict['id'], additional_claims=additional_claims)
            return {"message": "Login successful", "status": "success", "access_token": access_token, "user": user_dict}
        
        return {"message": "Invalid credentials", "status": "fail"}, 401