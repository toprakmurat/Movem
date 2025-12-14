from flask import Blueprint, jsonify, render_template, url_for
from src.services.movie_service import *
from src.services.users_service import *
from src.routes.actors import *
from src.services.comments_service import get_top_reviewers
from src.services.actors_service import get_featured_people_db

home_bp = Blueprint('home', __name__)


from src.services.statistic_service import get_cinemetrics_movies_db

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
        },
        {
            "title": "Time Capsule",
            "subtitle": "Best of Every Year",
            "image": base_image,
            "link_param": "time_capsule"
        },
        {
            "title": "Timeless",
            "subtitle": "Old but Gold",
            "image": base_image,
            "link_param": "timeless"
        }
    ]

    # fetch dynamic images for cinemetrics cards
    for option in discovery_options:
        movies_paginated, err = get_cinemetrics_movies_db(option['link_param'], page=1, per_page=1)
        if movies_paginated and movies_paginated.items:
            first_movie = movies_paginated.items[0]
            if first_movie.get('poster_file') or first_movie.get('poster_path'):
                option['image'] = url_for('static', filename='img/' + (first_movie.get('poster_file') or first_movie.get('poster_path')))

    best_movies, _ = get_best_movies_detailed_db(8)
    featured_movies, _ = get_random_movies_detailed_db(8)
    genres_available, _ = get_top_genres_db(10)
    genres_available = [g['genre_name'] for g in genres_available]

    featured_people, _ = get_featured_people_db(4)
    if not featured_people:
        featured_people = []
    
    best_movies_for_genres, _ = get_best_movies_for_genres_detailed_db(10,10)
    best_movies_for_genres = [dict(m) for m in best_movies_for_genres]

    top_reviewers, err = get_top_reviewers(limit=10)
    if not top_reviewers:
        top_reviewers = []

    data = {
        "trending_movies": best_movies,
        "random_movies": featured_movies,
        "genres": genres_available,
        "featured_collections": [
            {"id": 1, "title": "Award Winners", "count": 12},
            {"id": 2, "title": "Family Night", "count": 8},
        ],
        "featured_people": featured_people,
        "top_reviewers": top_reviewers,
        "home_movies": best_movies_for_genres,
        "discovery_options": discovery_options
    }
    return render_template("home.html", **data)