from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)

class CustomSerializer(SerializerMixin):
    def serialize(self, model):
        pass

class User(db.Model, SerializerMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='user') 

    serialize_rules = ('-password_hash',)
    serialize_only = ('id', 'username', 'email', 'role')

    projects = db.relationship('Project', backref='user', lazy=True)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

class Project(db.Model, SerializerMixin):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Add ForeignKey constraint
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),  # Convert to ISO 8601 string
            "updated_at": self.updated_at.isoformat()   # Convert to ISO 8601 string
        }

    serialize_only = ('id', 'title', 'description', 'created_at', 'updated_at')

    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model, SerializerMixin):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default='')
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    priority = db.Column(db.String(50), nullable=False, default='Normal')
    status = db.Column(db.String(50), nullable=False, default='Pending')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    serialize_only = ('id', 'title', 'description', 'due_date', 'priority', 'status', 'created_at', 'updated_at')

    tags = db.relationship('Tag', secondary='task_tags', lazy='subquery', backref=db.backref('tasks', lazy=True))
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat(),  # Convert to ISO 8601 string
            "priority": self.priority,
            "status": self.status,
            "project_id": self.project_id
        }
    
class Tag(db.Model, SerializerMixin):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class TaskTag(db.Model, SerializerMixin):
    __tablename__ = 'task_tags'

    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
