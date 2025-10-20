from flask import Blueprint, jsonify, render_template

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    """Movem home endpoint"""
    return render_template('home.html')