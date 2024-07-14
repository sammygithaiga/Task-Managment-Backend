import os
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import db
from resources.project import ProjectItemResource, ProjectListResource, ProjectResource
from resources.task import TaskResource
from resources.useer import LoginResource, SignupResource  # Fixed typo

app = Flask(__name__)

# Set your JWT_SECRET_KEY (ensure this is securely generated and kept secret)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Replace with your secret key

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

jwt_manager = JWTManager(app)
api = Api(app)

# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy database
db.init_app(app)

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db, render_as_batch=True)

# Ensure tables are created (for development/testing purposes)
with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello world"}

# Add API resources
api.add_resource(HelloWorld, '/')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(ProjectResource, '/project')
api.add_resource(ProjectItemResource, '/project/<int:project_id>')
api.add_resource(ProjectListResource, '/projects')
api.add_resource(TaskResource, '/task/<int:task_id>')

if __name__ == '__main__':
    app.run(port=5000)