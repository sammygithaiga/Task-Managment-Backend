from flask import Flask
from flask_jwt_extended import JWTManager

from flask_migrate import Migrate
from flask_restful import Resource, Api

from models import db,bcrypt, User, Project, Task, Tag, TaskTag
from resources.user import SignupResource, LoginResource
from resources.task import TaskResource, TaskListResource


app = Flask(__name__)
api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  #
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return { "message": "Hello world" }
    
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(TaskResource, '/tasks/<int:task_id>')
api.add_resource(TaskListResource, '/tasks')
    
    
if __name__ == '__main__':
    app.run