from db import db, ma
from marshmallow import fields

class RecipeModel(db.Model):
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    ingredients = db.Column(db.String(600))
    directions = db.Column(db.String(1000))

    def __init__(self, name, ingredients, directions):
        self.name = name
        self.ingredients = ingredients
        self.directions = directions

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'ingredients': self.ingredients,
            'directions': self.directions
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class RecipeSchema(ma.ModelSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    ingredients = fields.Str()
    directions = fields.Str()

    class Meta:
        ordered=True