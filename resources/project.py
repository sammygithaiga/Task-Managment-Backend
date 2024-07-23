from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project
from datetime import datetime

class ProjectResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', required=True, help="Title is required")
        self.parser.add_argument('description', required=True, help="Description is required")
        super(ProjectResource, self).__init__()

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        identity = get_jwt_identity()
        user_id = identity.get('id')  
        
        new_project = Project(
            title=data['title'],
            description=data['description'],
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return {"message": "Project created successfully", "project": new_project.to_dict()}, 201


class ProjectItemResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', required=True, help="Title is required")
        self.parser.add_argument('description', required=True, help="Description is required")
        super(ProjectItemResource, self).__init__()

    @jwt_required()
    def put(self, project_id):
        data = self.parser.parse_args()
        identity = get_jwt_identity()
        user_id = identity.get('id')  
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404

        project.title = data['title']
        project.description = data['description']
        project.updated_at = datetime.now()
        
        db.session.commit()
        
        return {"message": "Project updated successfully", "project": project.to_dict()}, 200

    @jwt_required()
    def delete(self, project_id):
        identity = get_jwt_identity()
        user_id = identity.get('id')  # Extract the user ID from the dictionary
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404
        
        db.session.delete(project)
        db.session.commit()
        
        return {"message": "Project deleted successfully"}, 200

    @jwt_required()
    def get(self, project_id):
        identity = get_jwt_identity()
        user_id = identity.get('id')  
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404
        
        return {"project": project.to_dict()}, 200


class ProjectListResource(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        user_id = identity.get('id')  
        projects = Project.query.filter_by(user_id=user_id).all()
        
        return {"projects": [project.to_dict() for project in projects]}, 200
