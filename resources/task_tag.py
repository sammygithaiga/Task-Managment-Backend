from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task, Tag, TaskTagAssociation, Project
from sqlalchemy.exc import IntegrityError

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
        if not project or project.user_id != current_user:
            return {"message": "Not authorized to add task to this project", "status": "fail"}, 403

        task = Task(
            title=data['title'],
            description=data.get('description'),
            due_date=data.get('due_date'),
            priority=data.get('priority'),
            status=data.get('status'),
            project_id=data['project_id']
        )

        try:
            db.session.add(task)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to create task", "status": "fail"}, 400

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

class TagResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True, help="Name is required")
    parser.add_argument('description', required=False, help="Description")

    @jwt_required()
    def get(self, tag_id):
        tag = Tag.query.get(tag_id)
        if tag:
            return {"tag": tag.to_dict(), "status": "success"}
        return {"message": "Tag not found", "status": "fail"}, 404

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        current_user = get_jwt_identity()

        tag = Tag(
            name=data['name'],
            description=data.get('description'),
            user_id=current_user
        )

        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to create tag", "status": "fail"}, 400

        return {"message": "Tag created successfully", "status": "success", "tag": tag.to_dict()}, 201

    @jwt_required()
    def put(self, tag_id):
        data = self.parser.parse_args()
        tag = Tag.query.get(tag_id)
        
        if not tag:
            return {"message": "Tag not found", "status": "fail"}, 404

        current_user = get_jwt_identity()
        if tag.user_id != current_user:
            return {"message": "Not authorized to update this tag", "status": "fail"}, 403

        tag.name = data['name']
        tag.description = data.get('description')

        db.session.commit()

        return {"message": "Tag updated successfully", "status": "success", "tag": tag.to_dict()}

    @jwt_required()
    def delete(self, tag_id):
        tag = Tag.query.get(tag_id)
        
        if not tag:
            return {"message": "Tag not found", "status": "fail"}, 404

        current_user = get_jwt_identity()
        if tag.user_id != current_user:
            return {"message": "Not authorized to delete this tag", "status": "fail"}, 403

        db.session.delete(tag)
        db.session.commit()

        return {"message": "Tag deleted successfully", "status": "success"}

class TaskTagAssociationResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('task_id', type=int, required=True, help="Task ID is required")
    parser.add_argument('tag_id', type=int, required=True, help="Tag ID is required")

    @jwt_required()
    def post(self):
        data = self.parser.parse_args()
        current_user = get_jwt_identity()

        task = Task.query.get(data['task_id'])
        if not task or task.project.user_id != current_user:
            return {"message": "Task not found or not authorized", "status": "fail"}, 403

        tag = Tag.query.get(data['tag_id'])
        if not tag or tag.user_id != current_user:
            return {"message": "Tag not found or not authorized", "status": "fail"}, 403

        existing_association = TaskTagAssociation.query.filter_by(task_id=data['task_id'], tag_id=data['tag_id']).first()
        if existing_association:
            return {"message": "Task-Tag association already exists", "status": "fail"}, 400

        association = TaskTagAssociation(
            task_id=data['task_id'],
            tag_id=data['tag_id']
        )

        try:
            db.session.add(association)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to create association", "status": "fail"}, 400

        return {"message": "Task-Tag association created successfully", "status": "success"}, 201

    @jwt_required()
    def delete(self):
        data = self.parser.parse_args()
        current_user = get_jwt_identity()

        association = TaskTagAssociation.query.filter_by(task_id=data['task_id'], tag_id=data['tag_id']).first()
        if not association:
            return {"message": "Task-Tag association not found", "status": "fail"}, 404

        task = Task.query.get(data['task_id'])
        if not task or task.project.user_id != current_user:
            return {"message": "Task not found or not authorized", "status": "fail"}, 403

        tag = Tag.query.get(data['tag_id'])
        if not tag or tag.user_id != current_user:
            return {"message": "Tag not found or not authorized", "status": "fail"}, 403

        db.session.delete(association)
        db.session.commit()

        return {"message": "Task-Tag association deleted successfully", "status": "success"}

class TaskListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        tasks = Task.query.join(Project).filter(Project.user_id == current_user).all()
        return {"tasks": [task.to_dict() for task in tasks], "status": "success"}

class TagListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        tags = Tag.query.filter_by(user_id=current_user).all()
        return {"tags": [tag.to_dict() for tag in tags], "status": "success"}
