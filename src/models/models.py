from src.config.database import db
from datetime import datetime


class Movie(db.Model):
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    type = db.Column(db.String(50))  # movie or series
    rating = db.Column(db.Float, default=0)
    poster_url = db.Column(db.String(255))
    genre = db.Column(db.String(100))
    platform = db.Column(db.String(100))  # Netflix, Prime, etc.
    cast_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with movie_cast
    cast_members = db.relationship('MovieCast', backref='movie', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'release_year': self.release_year,
            'type': self.type,
            'rating': self.rating,
            'poster_url': self.poster_url,
            'genre': self.genre,
            'platform': self.platform,
            'cast_id': self.cast_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Person(db.Model):
    __tablename__ = 'people'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with movie_cast
    movie_roles = db.relationship('MovieCast', backref='person', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'biography': self.biography,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MovieCast(db.Model):
    __tablename__ = 'movie_cast'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'), nullable=False)
    role = db.Column(db.String(100))  # actor, cameo, guest, etc.
    character_name = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'person_id': self.person_id,
            'role': self.role,
            'character_name': self.character_name
        }