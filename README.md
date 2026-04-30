# Vacation Rental Management System with Price Prediction

An undergraduate thesis MVP demonstrating a web-based vacation rental management system integrated with a machine learning price prediction module.

**Note:** This is an academic MVP project, not a production SaaS platform.

## Features & Modules

- **Authentication:** Secure login and registration.
- **Roles:** Role-based access for Administrator, Host, and Customer users.
- **Property Management:** Hosts can manage property listings.
- **Booking Management:** Customers can book properties; hosts manage booking confirmations.
- **Review Management:** Customers can submit reviews for their stays.
- **Admin Dashboard:** Administrators can monitor users, properties, bookings, and reviews.
- **ML Price Prediction:** Hosts can estimate a suitable nightly rental price based on property features using a trained Scikit-learn model.

## Technology Stack

- **Backend:** Flask (Python) with Flask-SQLAlchemy and Flask-Login.
- **Frontend:** HTML, CSS, JavaScript, and Jinja templates.
- **Database:** SQLite.
- **Machine Learning:** Scikit-learn, Pandas, Numpy, Joblib, Matplotlib.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:SabetAbderrahmane/Vacation-Rental-Management-System-with-Price-Prediction.git
   cd Vacation-Rental-Management-System-with-Price-Prediction
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   ```
   - *Windows PowerShell:* `.\.venv\Scripts\Activate.ps1`
   - *macOS/Linux:* `source .venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database:**
   Ensure the initialization script creates the SQLite database in the `instance/` folder.
   ```bash
   python init_db.py
   # or through the main app
   ```

## Running the Application

Start the Flask development server:

```bash
python app.py
```
Then navigate to `http://127.0.0.1:5000` in your web browser.

## Training the ML Model

To train the rental price prediction model, a public rental dataset must be placed in `ml/dataset/raw/listings.csv`. Then run:

```bash
python ml/train_model.py
```

This will generate the necessary prediction artifacts (`model.joblib`, `metrics.json`, `feature_schema.json`) for the backend to use.
