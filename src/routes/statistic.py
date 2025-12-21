from flask import Blueprint, jsonify, request, render_template
from src.services.statistic_service import (
    get_statistics_db,
    get_statistic_by_id_db,
    create_statistic_db,
    update_statistic_db,
    delete_statistic_db,
    get_cinemetrics_movies_db,
    get_platform_share_db,
    get_genre_popularity_db,
    get_release_timeline_db,
    get_runtime_trend_db,
    get_rating_distribution_db,
    get_seasonal_revenue_db,
    get_bankable_stars_db
)
from src.utils.decorators import admin_required

statistic_bp = Blueprint('statistic', __name__)

@statistic_bp.route('/cinemetrics/<string:metric_type>', methods=['GET'])
def cinemetrics_page(metric_type):
    """Render the cinemetrics page for a specific metric"""
    
    # Validation mapping
    valid_metrics = {
        'hidden_gems': ('Hidden Gems', 'Underrated movies with high ratings but lower popularity.'),
        'short': ('Short & Sweet', 'Movies under 90 minutes perfect for a quick watch.'),
        'critics': ("Critics' Choice", 'Highly acclaimed movies with over 8.0 rating.'),
        'revenue': ('Box Office Hits', 'Top grossing movies of all time.'),
        'time_capsule': ('The Time Capsule', 'The highest rated movie from every year.'),
        'timeless': ('Timeless Trending', 'Old classics active right now.')
    }
    
    if metric_type not in valid_metrics:
        return render_template('404.html'), 404
        
    title, subtitle = valid_metrics[metric_type]
    page = request.args.get('page', 1, type=int)
    
    movies, err = get_cinemetrics_movies_db(metric_type, page=page)
    
    if err:
        return render_template('500.html', error=err), 500
        
    return render_template(
        'cinemetrics.html', 
        movies=movies, 
        title=title, 
        subtitle=subtitle, 
        metric_type=metric_type
    )

@statistic_bp.route('/', methods=['GET'])
def get_statistics():
    """Get all statistics"""
    stats, err = get_statistics_db()
    if err:
        return jsonify({"error": err}), 500
    return jsonify([dict(s) for s in stats]), 200

@statistic_bp.route('/<int:movie_id>', methods=['GET'])
def get_statistic(movie_id):
    """Get statistic by movie_id"""
    stat, err = get_statistic_by_id_db(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not stat:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(stat)), 200

@statistic_bp.route('/', methods=['POST'])
@admin_required
def create_statistic():
    """Create a new statistic"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    new_stat, err = create_statistic_db(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(dict(new_stat)), 201

@statistic_bp.route('/<int:movie_id>', methods=['PUT'])
@admin_required
def update_statistic(movie_id):
    """Update statistic"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    updated, err = update_statistic_db(movie_id, data)
    if err:
        return jsonify({"error": err}), 400
    if not updated:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(updated)), 200

@statistic_bp.route('/<int:movie_id>', methods=['DELETE'])
@admin_required
def delete_statistic(movie_id):
    """Delete statistic"""
    deleted, err = delete_statistic_db(movie_id)
    if err:
        return jsonify({"error": err}), 500
    if not deleted:
        return jsonify({"message": "Statistic not found"}), 404
    return jsonify(dict(deleted)), 200

@statistic_bp.route('/analytics', methods=['GET'])
def analytics_page():
    """Render the analytics dashboard with chart data"""
    
    # platform share
    platforms, err1 = get_platform_share_db()
    
    # genre popularity
    genres, err2 = get_genre_popularity_db()
    
    # release timeline
    timeline, err3 = get_release_timeline_db()
    
    # runtime trend
    runtime_trend, err4 = get_runtime_trend_db()

    # rating distribution
    rating_dist, err5 = get_rating_distribution_db()

    # seasonal revenue
    seasonal_rev, err6 = get_seasonal_revenue_db()

    # bankable stars
    bankable_stars, err7 = get_bankable_stars_db()

    # error handling
    if any([err1, err2, err3, err4, err5, err6, err7]):
        print(f"Analytics Error: {err1} {err2} {err3} {err4} {err5} {err6} {err7}")

    return render_template(
        'analytics.html',
        platforms=platforms or [],
        genres=genres or [],
        timeline=timeline or [],
        runtime_trend=runtime_trend or [],
        rating_dist=rating_dist or [],
        seasonal_rev=seasonal_rev or [],
        bankable_stars=bankable_stars or []
    )
