
from app import db


class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    employees = db.relationship(
        "Employee",
        backref="department",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

