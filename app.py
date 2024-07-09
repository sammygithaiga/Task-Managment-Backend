import os
from flask import Flask


from flask_migrate import Migrate
from flask_restful import Resource, Api

from models import db,  User, Project, Task 



app = Flask(__name__)
api = Api(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  #
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

with app.app_context():
    db.create_all()

class HelloWorld(Resource):
    def get(self):
        return { "message": "Hello world" }
    
    
if __name__ == '__main__':
    app.run