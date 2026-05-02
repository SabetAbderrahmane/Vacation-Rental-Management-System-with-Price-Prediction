"""
init_db.py — Task 2.5

Creates all SQLite database tables by running SQLAlchemy's create_all().

Usage:
    python init_db.py

Safe to run multiple times — create_all() only creates tables that do not exist yet.
It will NOT drop or modify existing tables.
"""

from app import create_app
from models import db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")
    print("Database file: instance/app.db")
