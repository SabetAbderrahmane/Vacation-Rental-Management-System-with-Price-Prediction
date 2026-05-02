from models import db
from datetime import datetime


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    room_type = db.Column(db.String(50), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False, default=1)
    bathrooms = db.Column(db.Float, nullable=False, default=1.0)
    max_guests = db.Column(db.Integer, nullable=False, default=1)
    amenities = db.Column(db.Text, nullable=True)
    price_per_night = db.Column(db.Float, nullable=False)
    availability_status = db.Column(db.String(30), nullable=False, default="available")
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    bookings = db.relationship("Booking", backref="property", lazy=True)
    reviews = db.relationship("Review", backref="property", lazy=True)

    def __repr__(self):
        return f"<Property {self.title}>"
