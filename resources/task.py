from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, Project
from datetime import datetime

class TaskResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True, help="Title is required")
    parser.add_argument('description', required=True, help="Description")
    parser.add_argument('due_date', required=True, help="Due date")
    parser.add_argument('priority', required=True, help="Priority")
    parser.add_argument('status', required=True, help="Status")
    parser.add_argument('project_id', required=True, help="Project ID is required")

    @jwt_required()
    def get(self, task_id):
        task = Task.query.get(task_id)
        if task:
            return {"task": task.to_dict(), "status": "success"}, 200
        else:
            return {"message": "Task not found", "status": "fail"}, 404

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        current_user = get_jwt_identity()
        
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return {"message": "Invalid due date format. Please use 'YYYY-MM-DD'", "status": "fail"}, 400

        project = Project.query.get(data['project_id'])
        if not project:
            return {"message": "Project not found", "status": "fail"}, 404
        
        if project.user_id != int(current_user):
            return {"message": "Not authorized to add task to this project", "status": "fail"}, 403

        task = Task(
            title=data['title'],
            description=data['description'],
            due_date=due_date,
            priority=data['priority'],
            status=data['status'],
            project_id=data['project_id']
        )

        db.session.add(task)
        db.session.commit()

        return {"message": "Task created successfully", "status": "success", "task": task.to_dict()}, 201

    @jwt_required()
    def put(self, task_id):
        data = self.parser.parse_args()
        task = Task.query.get(task_id)
        
        if not task:
            return {"message": "Task not found", "status": "fail"}, 404

        current_user = get_jwt_identity()
        project = Project.query.get(task.project_id)
        if not project:
            return {"message": "Project not found", "status": "fail"}, 404
        
        if project.user_id != int(current_user):
            return {"message": "Not authorized to update this task", "status": "fail"}, 403

        task.title = data['title']
        task.description = data['description']
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return {"message": "Invalid due date format. Please use 'YYYY-MM-DD'", "status": "fail"}, 400
        task.priority = data['priority']
        task.status = data['status']

        db.session.commit()

        return {"message": "Task updated successfully", "status": "success", "task": task.to_dict()}

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get(task_id)
        
        if not task:
            return {"message": "Task not found", "status": "fail"}, 404

        current_user = get_jwt_identity()
        project = Project.query.get(task.project_id)
        if not project:
            return {"message": "Project not found", "status": "fail"}, 404
        
        if project.user_id != int(current_user):
            return {"message": "Not authorized to delete this task", "status": "fail"}, 403

        db.session.delete(task)
        db.session.commit()

        return {"message": "Task deleted successfully", "status": "success"}
