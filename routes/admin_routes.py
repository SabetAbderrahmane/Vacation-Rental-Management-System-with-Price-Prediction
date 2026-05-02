from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.property import Property
from models.booking import Booking
from models.review import Review
from routes.utils import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role="host").count()
    total_customers = User.query.filter_by(role="customer").count()
    total_properties = Property.query.count()
    total_bookings = Booking.query.count()
    total_reviews = Review.query.count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_hosts=total_hosts,
        total_customers=total_customers,
        total_properties=total_properties,
        total_bookings=total_bookings,
        total_reviews=total_reviews
    )


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/properties")
@login_required
@admin_required
def properties():
    all_properties = Property.query.order_by(Property.created_at.desc()).all()
    
    for p in all_properties:
        p._host = User.query.get(p.host_id)
        
    return render_template("admin/properties.html", properties=all_properties)


@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    
    for b in all_bookings:
        b._customer = User.query.get(b.customer_id)
        b._property = Property.query.get(b.property_id)
        
    return render_template("admin/bookings.html", bookings=all_bookings)


@admin_bp.route("/reviews")
@login_required
@admin_required
def reviews():
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    
    for r in all_reviews:
        r._customer = User.query.get(r.customer_id)
        r._property = Property.query.get(r.property_id)
        
    return render_template("admin/reviews.html", reviews=all_reviews)
