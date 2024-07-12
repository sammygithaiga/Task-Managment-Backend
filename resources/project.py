from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Project, User
from datetime import datetime


class ProjectResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help="Name is required")
    parser.add_argument('description', required=True, help="Description is required")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        user_id = get_jwt_identity()
        
        new_project = Project(
            name=data['name'],
            description=data['description'],
            user_id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return {"message": "Project created successfully", "project": new_project.to_dict()}, 201

    @jwt_required()
    def put(self, project_id):
        data = self.parser.parse_args()
        user_id = get_jwt_identity()
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404

        project.name = data['name']
        project.description = data['description']
        project.updated_at = datetime.now()
        
        db.session.commit()
        
        return {"message": "Project updated successfully", "project": project.to_dict()}, 200

    @jwt_required()
    def delete(self, project_id):
        user_id = get_jwt_identity()
        
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404
        
        db.session.delete(project)
        db.session.commit()
        
        return {"message": "Project deleted successfully"}, 200

    @jwt_required()
    def get(self, project_id):
        user_id = get_jwt_identity()
        
        # Find the project
        project = Project.query.filter_by(id=project_id, user_id=user_id).first()
        
        if not project:
            return {"message": "Project not found or not authorized"}, 404
        
        return {"project": project.to_dict()}, 200

class ProjectListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        
        # Get all projects for the user
        projects = Project.query.filter_by(user_id=user_id).all()
        
        return {"projects": [project.to_dict() for project in projects]}, 200