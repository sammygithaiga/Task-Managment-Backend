from datetime import datetime
from app import app
from models import db, User, Project, Task, Tag

with app.app_context():
    print("Start seeding...")
    
    
    Task.query.delete()
    Project.query.delete()
    User.query.delete()
    Tag.query.delete()

    
    print("Seeding users.....")
    user1 = User(username="Alice", email="alice@example.com", password_hash="password123")
    user3 = User(username="Bob", email="bob@example.com", password_hash="password123")
    user2 = User(username="Me", email="Me@example.com", password_hash="password123")
    db.session.add_all([user1, user2])
    db.session.commit()
    print("Users seeded......")

    
    print("Seeding projects")
    project1 = Project(title="Project Alpha", description="First project", user_id=user1.id, created_at=datetime.now(), updated_at=datetime.now())
    project2 = Project(title="Project Beta", description="Second project", user_id=user2.id, created_at=datetime.now(), updated_at=datetime.now())
    
    db.session.add_all([project1, project2])
    db.session.commit()
    print("Projects seeded....")

    
    print("Seeding tasks....")
    task1 = Task(title="Task 1", description="First task", due_date=datetime.now(), priority="High", status="Incomplete", project_id=project1.id, created_at=datetime.now(), updated_at=datetime.now())
    task2 = Task(title="Task 2", description="Second task", due_date=datetime.now(), priority="Medium", status="Incomplete", project_id=project2.id, created_at=datetime.now(), updated_at=datetime.now())
    
    db.session.add_all([task1, task2])
    db.session.commit()
    print("Tasks seeded.....")

    
    print("Seeding tags")
    tag1 = Tag(name="urgent")
    tag2 = Tag(name="important")
    
    db.session.add_all([tag1, tag2])
    db.session.commit()
    print("Tags seeded.......")

    
    print("Associating tasks with tags.....")
    task1.tags.append(tag1)
    task2.tags.append(tag2)
    
    db.session.commit()
    print("Tasks and tags associated......")

    print("Database seeded")
    print("Complete")
