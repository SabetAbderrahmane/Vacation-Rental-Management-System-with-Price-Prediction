from flask import Blueprint, render_template, request, abort
from models.property import Property
from models.review import Review

property_bp = Blueprint("property", __name__)


@property_bp.route("/")
def index():
    
    featured_properties = Property.query.filter_by(availability_status="available").order_by(
        Property.created_at.desc()
    ).limit(3).all()
    return render_template("index.html", featured_properties=featured_properties)


@property_bp.route("/properties")
def list_properties():
    query = Property.query.filter_by(availability_status="available")

    # Simple filters
    location = request.args.get("location", "").strip()
    if location:
        query = query.filter(Property.location.ilike(f"%{location}%"))

    room_type = request.args.get("room_type", "").strip()
    if room_type:
        query = query.filter_by(room_type=room_type)

    try:
        min_price = float(request.args.get("min_price", ""))
        query = query.filter(Property.price_per_night >= min_price)
    except ValueError:
        pass

    try:
        max_price = float(request.args.get("max_price", ""))
        query = query.filter(Property.price_per_night <= max_price)
    except ValueError:
        pass

    try:
        max_guests = int(request.args.get("max_guests", ""))
        query = query.filter(Property.max_guests >= max_guests)
    except ValueError:
        pass

    properties = query.order_by(Property.created_at.desc()).all()

    return render_template("properties/list.html", properties=properties)


@property_bp.route("/properties/<int:property_id>")
def property_detail(property_id):
    prop = Property.query.get_or_404(property_id)
    


    reviews = Review.query.filter_by(property_id=prop.id).order_by(Review.created_at.desc()).all()
    
    from models.user import User
    for r in reviews:
        r._customer = User.query.get(r.customer_id)

    return render_template("properties/detail.html", property=prop, reviews=reviews)
