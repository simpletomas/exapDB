from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)

    def __init__(self, first_name, last_name, email, password, country):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.country = country