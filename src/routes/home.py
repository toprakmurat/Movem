from flask import Blueprint, jsonify, render_template, url_for
from src.services.movie_service import *
from src.services.users_service import *
from src.routes.actors import *

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
@home_bp.route('/home')
def home():
    """Return home page"""
    base_image = url_for("static", filename="img/placeholder_poster.svg")

    discovery_options = [
        {
            "title": "Hidden Gems",
            "subtitle": "Underrated & Loved",
            "image": base_image,
            "link_param": "hidden_gems"
        },
        {
            "title": "Short & Sweet",
            "subtitle": "Under 90 Minutes",
            "image": base_image,
            "link_param": "short"
        },
        {
            "title": "Critics' Choice",
            "subtitle": "90%+ Rating",
            "image": base_image,
            "link_param": "critics"
        },
        {
            "title": "Box Office",
            "subtitle": "Top Earners",
            "image": base_image,
            "link_param": "revenue"
        }
    ]

    best_movies, _ = get_best_movies_detailed_db(3)
    featured_movies, _ = get_random_movies_detailed_db(8)
    genres_available, _ = get_genres_db()
    genres_available = [g['genre_name'] for g in genres_available]

    featured_people = [
    {"id": 1, "name": "John Doe", "photo_url": "/static/img/john.png", "known_for": "Action Movies"},
    {"id": 2, "name": "Jane Smith", "photo_url": "/static/img/jane.png", "known_for": "Comedy"},
    {"id": 3, "name": "Alice Green", "photo_url": "/static/img/alice.png", "known_for": "Drama"},
    {"id": 4, "name": "Bob Brown", "photo_url": "/static/img/bob.png", "known_for": "Sci-Fi"}
    ]
    best_movies_for_genres, _ = get_best_movies_detailed_db(60)
    best_movies_for_genres = [dict(m) for m in best_movies_for_genres]

    top_reviewers, _ = get_users_db()
    
    data = {
        "trending_movies": best_movies,
        "featured_movies": featured_movies,
        "genres": genres_available,
        "featured_collections": [
            {"id": 1, "title": "Award Winners", "count": 12},
            {"id": 2, "title": "Family Night", "count": 8},
        ],
        "featured_people": featured_people[:4],
        "top_reviewers": top_reviewers[:13],
        "home_movies": best_movies_for_genres,
        "discovery_options": discovery_options
    }
    return render_template("home.html", **data)