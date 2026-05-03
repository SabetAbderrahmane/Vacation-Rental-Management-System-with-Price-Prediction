import os
import json
import joblib
import pandas as pd
import numpy as np
from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
from routes.utils import host_required

prediction_bp = Blueprint("prediction", __name__)


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.joblib")
SCHEMA_PATH = os.path.join(BASE_DIR, "ml", "feature_schema.json")
METRICS_PATH = os.path.join(BASE_DIR, "ml", "metrics.json")

def load_ml_artifacts():
    """Helper to load model and schema safely."""
    model = None
    schema = None
    error = None

    if not os.path.exists(MODEL_PATH):
        error = f"Prediction model is not available at {MODEL_PATH}. Please train the model first."
        print(f"Prediction artifact error: {error}")
    elif not os.path.exists(SCHEMA_PATH):
        error = f"Feature schema is missing at {SCHEMA_PATH}. Please retrain the model."
        print(f"Prediction artifact error: {error}")
    else:
        try:
            model = joblib.load(MODEL_PATH)
            with open(SCHEMA_PATH, "r") as f:
                schema = json.load(f)
        except Exception as e:
            error = f"Error loading model artifacts: {str(e)}"
            print(f"Prediction artifact error: {error}")
    
    return model, schema, error

@prediction_bp.route("/host/predict", methods=["GET", "POST"])
@login_required
@host_required
def predict():
    model, schema, error = load_ml_artifacts()
    
    if request.method == "GET":
        if error:
            flash(error, "error")
        return render_template("host/predict_price.html", schema=schema, prediction=None, error_message=error)

  
    input_data = {}
    for key in request.form:
        input_data[key] = request.form.get(key)

    if error:
        flash(error, "error")
        return render_template("host/predict_price.html", 
                               schema=schema, 
                               prediction=None, 
                               form_data=input_data,
                               error_message=error)

    print("\n--- Prediction Debug Start ---")
    print(f"Received form keys: {list(request.form.keys())}")
    
    expected_features = schema.get("features", [])
    print(f"Expected feature names: {expected_features}")

    try:
       
        processed_inputs = {}
        
       
        for feat in schema.get("categorical_features", []):
            val = request.form.get(feat)
            if not val:
                print(f"Missing categorical field: {feat}")
                flash(f"Feature '{feat}' is required.", "error")
                return render_template("host/predict_price.html", schema=schema, prediction=None, form_data=input_data)
            processed_inputs[feat] = str(val)

      
        for feat in schema.get("numeric_features", []):
            val = request.form.get(feat)
            if val is None or val.strip() == "":
                print(f"Missing numeric field: {feat}")
                flash(f"Feature '{feat}' is required.", "error")
                return render_template("host/predict_price.html", schema=schema, prediction=None, form_data=input_data)
            try:
                processed_inputs[feat] = float(val)
            except ValueError:
                print(f"Invalid numeric value for {feat}: {val}")
                flash(f"Feature '{feat}' must be a numeric value.", "error")
                return render_template("host/predict_price.html", schema=schema, prediction=None, form_data=input_data)

       
        input_df = pd.DataFrame([processed_inputs])[expected_features]
        print(f"Constructed input_df columns: {list(input_df.columns)}")

        
        predicted_log = model.predict(input_df)[0]
        print(f"Raw log prediction: {predicted_log}")


        if schema.get("target_transform") == "natural_log":
            predicted_price = np.exp(predicted_log)
        else:
            predicted_price = predicted_log
        
        print(f"Converted prediction: {predicted_price}")

        # 5. Round
        final_price = round(float(predicted_price), 2)
        print(f"Final rounded price: {final_price}")
        print("--- Prediction Debug End ---\n")

        return render_template("host/predict_price.html", 
                               schema=schema, 
                               prediction=final_price, 
                               form_data=input_data)

    except Exception as e:
        print(f"EXCEPTION during prediction: {str(e)}")
        flash("Prediction failed because the input format does not match the trained model.", "error")
        return render_template("host/predict_price.html", schema=schema, prediction=None, form_data=input_data)

@prediction_bp.route("/host/predict/metrics")
@login_required
@host_required
def model_metrics():
    if not os.path.exists(METRICS_PATH):
        flash("Model metrics are not available.", "error")
        return render_template("host/model_metrics.html", metrics=None)

    try:
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
            
       
        importance = None
        imp_path = os.path.join("ml", "feature_importance.json")
        if os.path.exists(imp_path):
            with open(imp_path, "r") as f:
                importance = json.load(f)
                
        return render_template("host/model_metrics.html", metrics=metrics, importance=importance)
    except Exception as e:
        flash(f"Error loading metrics: {str(e)}", "error")
        return render_template("host/model_metrics.html", metrics=None)
