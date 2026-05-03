from app import create_app
from models import db
from models.user import User
from models.property import Property
from models.booking import Booking
from models.review import Review
from datetime import datetime, timedelta
import os

def seed_data():
    app = create_app()
    with app.app_context():
        print("Starting Database Seeding (Phase 13)...")
        
        # 1. Cleanup Order: Reviews -> Bookings -> Properties -> Users
        demo_emails = [
            "admin@example.com",
            "host@example.com",
            "host2@example.com",
            "customer@example.com",
            "customer2@example.com"
        ]
        
        # Identity targets
        target_users = User.query.filter(User.email.in_(demo_emails)).all()
        target_user_ids = [u.id for u in target_users]
        
        if target_user_ids:
            # Delete Reviews
            # (Either by demo customers or on demo properties)
            demo_props = Property.query.filter(Property.host_id.in_(target_user_ids)).all()
            demo_prop_ids = [p.id for p in demo_props]
            
            Review.query.filter(
                (Review.customer_id.in_(target_user_ids)) | 
                (Review.property_id.in_(demo_prop_ids))
            ).delete(synchronize_session=False)
            
            # Delete Bookings
            Booking.query.filter(
                (Booking.customer_id.in_(target_user_ids)) |
                (Booking.property_id.in_(demo_prop_ids))
            ).delete(synchronize_session=False)
            
            # Delete Properties
            Property.query.filter(Property.host_id.in_(target_user_ids)).delete(synchronize_session=False)
            
            # Delete Users
            User.query.filter(User.email.in_(demo_emails)).delete(synchronize_session=False)
            
            db.session.commit()
            print(f"Cleared existing demo records for: {', '.join(demo_emails)}")
        else:
            print("No existing demo records found. Proceeding with fresh creation.")

        # 2. Create Users
        # Admin
        admin = User(name="System Admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        
        # Hosts
        host1 = User(name="Sebastian Host", email="host@example.com", role="host", phone_number="123-456-7890")
        host1.set_password("host123")
        
        host2 = User(name="Sarah Host", email="host2@example.com", role="host", phone_number="098-765-4321")
        host2.set_password("host123")
        
        # Customers
        cust1 = User(name="Charles Guest", email="customer@example.com", role="customer")
        cust1.set_password("customer123")
        
        cust2 = User(name="Catherine Guest", email="customer2@example.com", role="customer")
        cust2.set_password("customer123")
        
        db.session.add_all([admin, host1, host2, cust1, cust2])
        db.session.commit()
        print(f"Created/Recreated {len(demo_emails)} demo users.")

        # 3. Create Properties (6 total)
        properties_data = [
            # Host 1 Properties
            {
                "host_id": host1.id,
                "title": "Brooklyn Heights Modern Studio",
                "description": "A sleek studio in the heart of Brooklyn Heights with Manhattan views.",
                "location": "Brooklyn Heights",
                "address": "123 Montague St, Brooklyn, NY 11201",
                "room_type": "entire_home",
                "bedrooms": 1,
                "bathrooms": 1.0,
                "max_guests": 2,
                "amenities": "WiFi, Kitchen, AC, TV, Workspace",
                "price_per_night": 175.0,
                "availability_status": "available",
                "image_url": "images/properties/nyc_brooklyn_apartment.jpg"
            },
            {
                "host_id": host1.id,
                "title": "Hollywood Hills Luxury Suite",
                "description": "Luxury suite with pool access and canyon views.",
                "location": "Hollywood",
                "address": "456 Mulholland Dr, Los Angeles, CA 90068",
                "room_type": "private_room",
                "bedrooms": 1,
                "bathrooms": 1.5,
                "max_guests": 2,
                "amenities": "Pool, WiFi, Parking, AC",
                "price_per_night": 250.0,
                "availability_status": "available",
                "image_url": "images/properties/la_hollywood_studio.jpg"
            },
            {
                "host_id": host1.id,
                "title": "Mission District Garden Loft",
                "description": "Spacious loft with a private garden in the vibrant Mission.",
                "location": "Mission District",
                "address": "789 Valencia St, San Francisco, CA 94110",
                "room_type": "entire_home",
                "bedrooms": 1,
                "bathrooms": 1.0,
                "max_guests": 3,
                "amenities": "Garden, WiFi, Kitchen, Washer",
                "price_per_night": 190.0,
                "availability_status": "available",
                "image_url": "images/properties/sf_mission_loft.jpg"
            },
            # Host 2 Properties
            {
                "host_id": host2.id,
                "title": "Columbia Heights Classic Rowhouse",
                "description": "Classic DC rowhouse charm with modern amenities.",
                "location": "Columbia Heights",
                "address": "1011 14th St NW, Washington, DC 20009",
                "room_type": "entire_home",
                "bedrooms": 3,
                "bathrooms": 2.5,
                "max_guests": 6,
                "amenities": "Kitchen, WiFi, Patio, AC, Heating",
                "price_per_night": 320.0,
                "availability_status": "available",
                "image_url": "images/properties/dc_columbia_home.jpg"
            },
            {
                "host_id": host2.id,
                "title": "Lakeview Chicago Apartment",
                "description": "Bright apartment near Wrigley Field and the lakefront.",
                "location": "Lakeview",
                "address": "2022 N Sheffield Ave, Chicago, IL 60614",
                "room_type": "entire_home",
                "bedrooms": 2,
                "bathrooms": 1.0,
                "max_guests": 4,
                "amenities": "WiFi, Kitchen, TV, Elevator",
                "price_per_night": 150.0,
                "availability_status": "available",
                "image_url": "images/properties/chicago_lakeview_condo.jpg"
            },
            {
                "host_id": host2.id,
                "title": "Beacon Hill Historic Flat",
                "description": "Historic flat on a cobblestone street in Boston.",
                "location": "Boston",
                "address": "303 Charles St, Boston, MA 02114",
                "room_type": "private_room",
                "bedrooms": 1,
                "bathrooms": 1.0,
                "max_guests": 2,
                "amenities": "WiFi, Desk, Historic Charm",
                "price_per_night": 130.0,
                "availability_status": "available",
                "image_url": "images/properties/boston_beacon_hill_room.jpg"
            }
        ]
        
        created_props = []
        for p_data in properties_data:
            prop = Property(**p_data)
            db.session.add(prop)
            created_props.append(prop)
        
        db.session.commit()
        print(f"Created {len(created_props)} demo properties.")

        # 4. Create Bookings (4 total)
        # Booking 1: Completed (Host 1, Prop 1, Cust 1)
        b1 = Booking(
            property_id=created_props[0].id,
            customer_id=cust1.id,
            check_in_date=(datetime.utcnow() - timedelta(days=10)).date(),
            check_out_date=(datetime.utcnow() - timedelta(days=7)).date(),
            number_of_nights=3,
            total_price=3 * created_props[0].price_per_night,
            status="completed"
        )
        
        # Booking 2: Confirmed (Host 2, Prop 4, Cust 1)
        b2 = Booking(
            property_id=created_props[3].id,
            customer_id=cust1.id,
            check_in_date=(datetime.utcnow() + timedelta(days=5)).date(),
            check_out_date=(datetime.utcnow() + timedelta(days=8)).date(),
            number_of_nights=3,
            total_price=3 * created_props[3].price_per_night,
            status="confirmed"
        )
        
        # Booking 3: Pending (Host 1, Prop 2, Cust 2)
        b3 = Booking(
            property_id=created_props[1].id,
            customer_id=cust2.id,
            check_in_date=(datetime.utcnow() + timedelta(days=12)).date(),
            check_out_date=(datetime.utcnow() + timedelta(days=14)).date(),
            number_of_nights=2,
            total_price=2 * created_props[1].price_per_night,
            status="pending"
        )
        
        # Booking 4: Cancelled (Host 2, Prop 5, Cust 2)
        b4 = Booking(
            property_id=created_props[4].id,
            customer_id=cust2.id,
            check_in_date=(datetime.utcnow() - timedelta(days=2)).date(),
            check_out_date=(datetime.utcnow() + timedelta(days=1)).date(),
            number_of_nights=3,
            total_price=3 * created_props[4].price_per_night,
            status="cancelled"
        )
        
        db.session.add_all([b1, b2, b3, b4])
        db.session.commit()
        print(f"Created 4 demo bookings (Completed, Confirmed, Pending, Cancelled).")

        # 5. Create Reviews (3 total)
        # Attached to completed/existing bookings where possible
        r1 = Review(
            property_id=created_props[0].id,
            customer_id=cust1.id,
            booking_id=b1.id,
            rating=5,
            comment="Amazing stay! the Manhattan view from Brooklyn Heights is breathtaking."
        )
        
        r2 = Review(
            property_id=created_props[3].id,
            customer_id=cust2.id,
            # (Simulated review without explicit completed booking ID for variety, if model allows)
            booking_id=None, 
            rating=4,
            comment="Great rowhouse, very authentic DC experience."
        )
        
        r3 = Review(
            property_id=created_props[4].id,
            customer_id=cust1.id,
            booking_id=None,
            rating=3,
            comment="Decent apartment, a bit noisy but great location."
        )
        
        db.session.add_all([r1, r2, r3])
        db.session.commit()
        print(f"Created 3 demo reviews.")
        
        print("\nSeeding Complete! Use the following credentials:")
        print("Admin: admin@example.com / admin123")
        print("Host: host@example.com / host123")
        print("Customer: customer@example.com / customer123")

if __name__ == "__main__":
    seed_data()
