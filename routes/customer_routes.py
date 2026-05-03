from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from models import db
from models.property import Property
from models.booking import Booking
from routes.utils import customer_required

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_bp.route("/dashboard")
@login_required
@customer_required
def dashboard():
    my_bookings = Booking.query.filter_by(customer_id=current_user.id).all()
    
    my_bookings_count = len(my_bookings)
    pending_bookings_count = sum(1 for b in my_bookings if b.status == "pending")
    confirmed_bookings_count = sum(1 for b in my_bookings if b.status == "confirmed")
    completed_bookings_count = sum(1 for b in my_bookings if b.status == "completed")

    return render_template(
        "customer/dashboard.html",
        my_bookings_count=my_bookings_count,
        pending_bookings_count=pending_bookings_count,
        confirmed_bookings_count=confirmed_bookings_count,
        completed_bookings_count=completed_bookings_count,
    )


@customer_bp.route("/bookings")
@login_required
@customer_required
def bookings():
    customer_bookings = Booking.query.filter_by(customer_id=current_user.id).order_by(
        Booking.created_at.desc()
    ).all()
   
    return render_template("customer/my_bookings.html", bookings=customer_bookings)


@customer_bp.route("/properties/<int:property_id>/book", methods=["GET", "POST"])
@login_required
@customer_required
def book_property(property_id):
    prop = Property.query.get_or_404(property_id)
    
    if prop.availability_status != "available":
        flash("This property is currently unavailable.", "error")
        return redirect(url_for("property.property_detail", property_id=prop.id))

    if request.method == "POST":
        check_in_str = request.form.get("check_in_date")
        check_out_str = request.form.get("check_out_date")

        if not check_in_str or not check_out_str:
            flash("Check-in and check-out dates are required.", "error")
            return render_template("customer/book_property.html", property=prop)

        try:
            check_in_date = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format.", "error")
            return render_template("customer/book_property.html", property=prop)

        if check_out_date <= check_in_date:
            flash("Check-out date must be after check-in date.", "error")
            return render_template("customer/book_property.html", property=prop)

        number_of_nights = (check_out_date - check_in_date).days
        total_price = number_of_nights * prop.price_per_night

        booking = Booking(
            property_id=prop.id,
            customer_id=current_user.id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            number_of_nights=number_of_nights,
            total_price=total_price,
            status="pending"
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash("Booking request submitted successfully.", "success")
        return redirect(url_for("customer.bookings"))

    return render_template("customer/book_property.html", property=prop)


@customer_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
@customer_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.customer_id != current_user.id:
        flash("You do not have permission to access this page.", "error")
        abort(403)

    booking.status = "cancelled"
    db.session.commit()
    
    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("customer.bookings"))


# ---------- Customer Reviews ----------

@customer_bp.route("/bookings/<int:booking_id>/review", methods=["GET", "POST"])
@login_required
@customer_required
def submit_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.customer_id != current_user.id:
        flash("You do not have permission to access this page.", "error")
        abort(403)

    if booking.status != "completed":
        flash("You can only review completed bookings.", "error")
        return redirect(url_for("customer.bookings"))

    from models.review import Review
    existing_review = Review.query.filter_by(booking_id=booking.id).first()
    if existing_review:
        flash("You have already submitted a review for this booking.", "error")
        return redirect(url_for("customer.bookings"))

    prop = Property.query.get(booking.property_id)

    if request.method == "POST":
        try:
            rating = int(request.form.get("rating", 0))
        except ValueError:
            rating = 0

        comment = request.form.get("comment", "").strip()

        if rating < 1 or rating > 5:
            flash("Please provide a valid rating between 1 and 5.", "error")
            return render_template("customer/submit_review.html", booking=booking, property=prop)

        new_review = Review(
            property_id=booking.property_id,
            customer_id=current_user.id,
            booking_id=booking.id,
            rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.commit()

        flash("Review submitted successfully.", "success")
        return redirect(url_for("property.property_detail", property_id=booking.property_id))

    return render_template("customer/submit_review.html", booking=booking, property=prop)
