from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db
from resources.project import ProjectResource
from resources.useer import LoginResource, SignupResource
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'uper-secret'  # Change this to a secret key

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


if __name__ == '__main__':
    app.run(port=5000)
