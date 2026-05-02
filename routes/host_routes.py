from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.property import Property
from models.booking import Booking
from routes.utils import host_required

host_bp = Blueprint("host", __name__, url_prefix="/host")

ALLOWED_ROOM_TYPES = ["entire_home", "private_room", "shared_room", "hotel_room"]
ALLOWED_STATUSES = ["available", "unavailable"]


# ---------- Dashboard ----------

@host_bp.route("/dashboard")
@login_required
@host_required
def dashboard():
    my_properties = Property.query.filter_by(host_id=current_user.id).all()
    property_ids = [p.id for p in my_properties]

    my_properties_count = len(my_properties)

    # Booking stats — safe even if no bookings exist yet
    if property_ids:
        my_bookings_count = Booking.query.filter(Booking.property_id.in_(property_ids)).count()
        pending_bookings_count = Booking.query.filter(
            Booking.property_id.in_(property_ids), Booking.status == "pending"
        ).count()
        completed_bookings_count = Booking.query.filter(
            Booking.property_id.in_(property_ids), Booking.status == "completed"
        ).count()
    else:
        my_bookings_count = 0
        pending_bookings_count = 0
        completed_bookings_count = 0

    return render_template(
        "host/dashboard.html",
        my_properties_count=my_properties_count,
        my_bookings_count=my_bookings_count,
        pending_bookings_count=pending_bookings_count,
        completed_bookings_count=completed_bookings_count,
    )


# ---------- My Properties List ----------

@host_bp.route("/properties")
@login_required
@host_required
def properties():
    my_properties = Property.query.filter_by(host_id=current_user.id).order_by(
        Property.created_at.desc()
    ).all()
    return render_template("host/my_properties.html", properties=my_properties)


# ---------- Add Property ----------

@host_bp.route("/properties/add", methods=["GET", "POST"])
@login_required
@host_required
def add_property():
    if request.method == "POST":
        # Collect form data
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        address = request.form.get("address", "").strip()
        room_type = request.form.get("room_type", "")
        amenities = request.form.get("amenities", "").strip()
        availability_status = request.form.get("availability_status", "available")
        image_url = request.form.get("image_url", "").strip() or None

        # Numeric fields with safe defaults
        try:
            bedrooms = int(request.form.get("bedrooms", 1))
        except (ValueError, TypeError):
            bedrooms = -1
        try:
            bathrooms = float(request.form.get("bathrooms", 1))
        except (ValueError, TypeError):
            bathrooms = -1
        try:
            max_guests = int(request.form.get("max_guests", 1))
        except (ValueError, TypeError):
            max_guests = 0
        try:
            price_per_night = float(request.form.get("price_per_night", 0))
        except (ValueError, TypeError):
            price_per_night = 0

        # Validation (per API_CONTRACTS.md section 5.4)
        if not title or len(title) < 3 or len(title) > 150:
            flash("Title is required (3-150 characters).", "error")
            return render_template("host/add_property.html")
        if not location or len(location) < 2 or len(location) > 150:
            flash("Location is required (2-150 characters).", "error")
            return render_template("host/add_property.html")
        if room_type not in ALLOWED_ROOM_TYPES:
            flash("Invalid room type.", "error")
            return render_template("host/add_property.html")
        if bedrooms < 0:
            flash("Bedrooms must be zero or greater.", "error")
            return render_template("host/add_property.html")
        if bathrooms < 0:
            flash("Bathrooms must be zero or greater.", "error")
            return render_template("host/add_property.html")
        if max_guests < 1:
            flash("Maximum guests must be at least 1.", "error")
            return render_template("host/add_property.html")
        if price_per_night <= 0:
            flash("Price per night must be greater than 0.", "error")
            return render_template("host/add_property.html")
        if availability_status not in ALLOWED_STATUSES:
            flash("Invalid availability status.", "error")
            return render_template("host/add_property.html")

        prop = Property(
            host_id=current_user.id,
            title=title,
            description=description,
            location=location,
            address=address,
            room_type=room_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            max_guests=max_guests,
            amenities=amenities,
            price_per_night=price_per_night,
            availability_status=availability_status,
            image_url=image_url,
        )
        db.session.add(prop)
        db.session.commit()
        flash("Property created successfully.", "success")
        return redirect(url_for("host.properties"))

    return render_template("host/add_property.html")


# ---------- Edit Property ----------

@host_bp.route("/properties/<int:property_id>/edit", methods=["GET", "POST"])
@login_required
@host_required
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)

    if prop.host_id != current_user.id:
        flash("You do not have permission to access this page.", "error")
        abort(403)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        address = request.form.get("address", "").strip()
        room_type = request.form.get("room_type", "")
        amenities = request.form.get("amenities", "").strip()
        availability_status = request.form.get("availability_status", "available")
        image_url = request.form.get("image_url", "").strip() or None

        try:
            bedrooms = int(request.form.get("bedrooms", 1))
        except (ValueError, TypeError):
            bedrooms = -1
        try:
            bathrooms = float(request.form.get("bathrooms", 1))
        except (ValueError, TypeError):
            bathrooms = -1
        try:
            max_guests = int(request.form.get("max_guests", 1))
        except (ValueError, TypeError):
            max_guests = 0
        try:
            price_per_night = float(request.form.get("price_per_night", 0))
        except (ValueError, TypeError):
            price_per_night = 0

        # Validation
        if not title or len(title) < 3 or len(title) > 150:
            flash("Title is required (3-150 characters).", "error")
            return render_template("host/edit_property.html", property=prop)
        if not location or len(location) < 2 or len(location) > 150:
            flash("Location is required (2-150 characters).", "error")
            return render_template("host/edit_property.html", property=prop)
        if room_type not in ALLOWED_ROOM_TYPES:
            flash("Invalid room type.", "error")
            return render_template("host/edit_property.html", property=prop)
        if bedrooms < 0:
            flash("Bedrooms must be zero or greater.", "error")
            return render_template("host/edit_property.html", property=prop)
        if bathrooms < 0:
            flash("Bathrooms must be zero or greater.", "error")
            return render_template("host/edit_property.html", property=prop)
        if max_guests < 1:
            flash("Maximum guests must be at least 1.", "error")
            return render_template("host/edit_property.html", property=prop)
        if price_per_night <= 0:
            flash("Price per night must be greater than 0.", "error")
            return render_template("host/edit_property.html", property=prop)
        if availability_status not in ALLOWED_STATUSES:
            flash("Invalid availability status.", "error")
            return render_template("host/edit_property.html", property=prop)

        prop.title = title
        prop.description = description
        prop.location = location
        prop.address = address
        prop.room_type = room_type
        prop.bedrooms = bedrooms
        prop.bathrooms = bathrooms
        prop.max_guests = max_guests
        prop.amenities = amenities
        prop.price_per_night = price_per_night
        prop.availability_status = availability_status
        prop.image_url = image_url
        db.session.commit()

        flash("Property updated successfully.", "success")
        return redirect(url_for("host.properties"))

    return render_template("host/edit_property.html", property=prop)


# ---------- Delete Property ----------

@host_bp.route("/properties/<int:property_id>/delete", methods=["POST"])
@login_required
@host_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)

    if prop.host_id != current_user.id:
        flash("You do not have permission to access this page.", "error")
        abort(403)

    # MVP delete rule: soft-delete if bookings exist
    booking_count = Booking.query.filter_by(property_id=prop.id).count()
    if booking_count > 0:
        prop.availability_status = "unavailable"
        db.session.commit()
        flash("Property has bookings, so it was marked unavailable instead of deleted.", "warning")
    else:
        db.session.delete(prop)
        db.session.commit()
        flash("Property deleted successfully.", "success")

    return redirect(url_for("host.properties"))


# ---------- Host Bookings ----------

@host_bp.route("/bookings")
@login_required
@host_required
def bookings():
    # Load bookings for properties owned by current host
    host_properties = Property.query.filter_by(host_id=current_user.id).all()
    prop_ids = [p.id for p in host_properties]
    
    # Needs to order by dates or created, MVP default desc based on creation
    host_bookings = Booking.query.filter(Booking.property_id.in_(prop_ids)).order_by(
        Booking.created_at.desc()
    ).all()
    
    # We will need the customer user objects in the template
    # Since we didn't add explicit bidirectional relationships everywhere in MVP phase 2,
    # we'll inject the customer object onto each booking dynamically for the template
    from models.user import User
    for b in host_bookings:
        b._customer = User.query.get(b.customer_id)
        
    return render_template("host/property_bookings.html", bookings=host_bookings)


@host_bp.route("/bookings/<int:booking_id>/confirm", methods=["POST"])
@login_required
@host_required
def confirm_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    prop = Property.query.get(booking.property_id)
    
    if not prop or prop.host_id != current_user.id:
        flash("You do not have permission to access this booking.", "error")
        abort(403)
        
    if booking.status != "pending":
        flash("Only pending bookings can be confirmed.", "error")
    else:
        booking.status = "confirmed"
        db.session.commit()
        flash("Booking confirmed successfully.", "success")
        
    return redirect(url_for("host.bookings"))


@host_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@host_required
def cancel_booking_host(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    prop = Property.query.get(booking.property_id)
    
    if not prop or prop.host_id != current_user.id:
        flash("You do not have permission to access this booking.", "error")
        abort(403)
        
    if booking.status not in ["pending", "confirmed"]:
        flash("Only pending or confirmed bookings can be cancelled.", "error")
    else:
        booking.status = "cancelled"
        db.session.commit()
        flash("Booking cancelled successfully.", "success")
        
    return redirect(url_for("host.bookings"))


@host_bp.route("/bookings/<int:booking_id>/complete", methods=["POST"])
@login_required
@host_required
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    prop = Property.query.get(booking.property_id)
    
    if not prop or prop.host_id != current_user.id:
        flash("You do not have permission to access this booking.", "error")
        abort(403)
        
    if booking.status != "confirmed":
        flash("Only confirmed bookings can be marked as completed.", "error")
    else:
        booking.status = "completed"
        db.session.commit()
        flash("Booking marked as completed.", "success")
        
    return redirect(url_for("host.bookings"))



# --- End of Routes ---

