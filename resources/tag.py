from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Tag
from sqlalchemy.exc import IntegrityError

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

        new_tag = Tag(
            name=data['name'],
            description=data.get('description'),
            user_id=current_user
        )

        try:
            db.session.add(new_tag)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to create tag", "status": "fail"}, 400

        return {"message": "Tag created successfully", "status": "success", "tag": new_tag.to_dict()}, 201

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

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to update tag", "status": "fail"}, 400

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

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Failed to delete tag", "status": "fail"}, 400

        return {"message": "Tag deleted successfully", "status": "success"}

class TagListResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        tags = Tag.query.filter_by(user_id=current_user).all()
        return {"tags": [tag.to_dict() for tag in tags], "status": "success"}
