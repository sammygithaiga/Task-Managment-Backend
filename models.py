from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy





convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}


metaData = MetaData(naming_convention = convention)

db = SQLAlchemy(metadata = metaData)


class User(db.Model, SerializerMixin):
    
    __tablename__ = 'user'
    
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    profile_picture = db.Column(db.String, nullable=True)
    
    
    serialize_rules = ('-password',)

   
    
    
    projects = db.relationship('Project', backref='user', lazy=True)
    
    
class Project(db.Model, SerializerMixin):
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String, nullable=False) 
    description = db.Column(db.Text, nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    created_at = db.Column(db.TIMESTAMP, nullable=False)
    updated_at = db.Column(db.TIMESTAMP, nullable=False) 
    
    tasks = db.relationship('Task', backref='project', lazy=True)
    
    
class Task(db.Model, SerializerMixin):
    __tablename__ = 'task'
    
    
    
    
    id = db.Column(db.Integer, primary_key=True) 
    title = db.Column(db.String, nullable=False)  
    description = db.Column(db.Text, nullable=True)  
    due_date = db.Column(db.DateTime, nullable=True)  
    priority = db.Column(db.String, nullable=True) 
    status = db.Column(db.String, nullable=True)  
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False) 
    created_at = db.Column(db.Date, nullable=False)  
    updated_at = db.Column(db.Date, nullable=False)  
    
    
    
    tags = db.relationship('Tag', secondary='task_tags', lazy='subquery', backref=db.backref('tasks', lazy=True))
    
   
class Tag(db.Model):
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(50), unique=True, nullable=False)  

class TaskTag(db.Model):
    __tablename__ = 'task_tags'
    
    id = db.Column(db.Integer, primary_key=True)  
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)  
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False) 