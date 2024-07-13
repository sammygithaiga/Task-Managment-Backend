import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import db
from resources.project import ProjectItemResource, ProjectListResource, ProjectResource
from resources.useer import LoginResource, SignupResource

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'b1c6dd628b391a653ef79c14d96acae5d1103dad006b441ab6fb2c203b4a3b28'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

jwt_manager = JWTManager(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db, render_as_batch=True)

with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello world"}

api.add_resource(HelloWorld, '/')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(ProjectResource, '/project')
api.add_resource(ProjectItemResource, '/project/<int:project_id>')
api.add_resource(ProjectListResource, '/projects')

secret_key = os.urandom(32).hex()
print(f"Generated JWT_SECRET_KEY: {secret_key}")

if __name__ == '__main__':
    app.run(port=5000)
