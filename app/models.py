from app import db


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Not Started')
    category = db.Column(db.String(50), default='General')

    def __repr__(self):
        return f'<Task {self.title}>'
