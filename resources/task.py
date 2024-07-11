from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, Project

class TaskResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True, help="Title is required")
    parser.add_argument('description', required=False, help="Description")
    parser.add_argument('due_date', required=False, help="Due date")
    parser.add_argument('priority', required=False, help="Priority")
    parser.add_argument('status', required=False, help="Status")
    parser.add_argument('project_id', required=True, help="Project ID is required")

    @jwt_required()
    def get(self, task_id):
        task = Task.query.get(task_id)
        if task:
            return {"task": task.to_dict(), "status": "success"}
        return {"message": "Task not found", "status": "fail"}, 404

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        current_user = get_jwt_identity()

        project = Project.query.get(data['project_id'])
        if project.user_id != current_user:
            return {"message": "Not authorized to add task to this project", "status": "fail"}, 403

        task = Task(
            title=data['title'],
            description=data.get('description'),
            due_date=data.get('due_date'),
            priority=data.get('priority'),
            status=data.get('status'),
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
        if project.user_id != current_user:
            return {"message": "Not authorized to update this task", "status": "fail"}, 403

        task.title = data['title']
        task.description = data.get('description')
        task.due_date = data.get('due_date')
        task.priority = data.get('priority')
        task.status = data.get('status')

        db.session.commit()

        return {"message": "Task updated successfully", "status": "success", "task": task.to_dict()}

    @jwt_required()
    def delete(self, task_id):
        task = Task.query.get(task_id)
        
        if not task:
            return {"message": "Task not found", "status": "fail"}, 404

        current_user = get_jwt_identity()
        project = Project.query.get(task.project_id)
        if project.user_id != current_user:
            return {"message": "Not authorized to delete this task", "status": "fail"}, 403

        db.session.delete(task)
        db.session.commit()

        return {"message": "Task deleted successfully", "status": "success"}

class TaskListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        tasks = Task.query.join(Project).filter(Project.user_id == current_user).all()
        return {"tasks": [task.to_dict() for task in tasks], "status": "success"}