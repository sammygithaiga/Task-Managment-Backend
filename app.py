import os
from flask import Flask
from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import db
from resources.project import ProjectItemResource, ProjectListResource, ProjectResource
from resources.task import TaskResource, TaskListResource, TaskItemResource
from resources.task import TaskResource,TaskListResource
from resources.useer import LoginResource, SignupResource, AdminResource, ProtectedResource

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

jwt_manager = JWTManager(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

migrate = Migrate(app, db, render_as_batch=True)

with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello world"}

api.add_resource(HelloWorld, '/')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(AdminResource, '/admin')
api.add_resource(ProtectedResource, '/protected')
api.add_resource(ProjectResource, '/project')
api.add_resource(ProjectItemResource, '/project/<int:project_id>')
api.add_resource(ProjectListResource, '/projects')
api.add_resource(TaskResource, '/task')
api.add_resource(TaskItemResource, '/task/<int:task_id>')
api.add_resource(TaskResource, '/tasks', '/tasks/<int:task_id>')
api.add_resource(TaskListResource, '/tasks')

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

if __name__ == '__main__':
    app.run(port=5000)