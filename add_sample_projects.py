from app import app
from models import db, Project

sample_projects = [
    {"code": "PRJ001", "name": "Website Redesign"},
    {"code": "PRJ002", "name": "Mobile App Development"},
    {"code": "PRJ003", "name": "Marketing Campaign"},
]

with app.app_context():
    for proj in sample_projects:
        if not Project.query.filter_by(code=proj["code"]).first():
            db.session.add(Project(code=proj["code"], name=proj["name"]))
    db.session.commit()
print("Sample projects added.")
