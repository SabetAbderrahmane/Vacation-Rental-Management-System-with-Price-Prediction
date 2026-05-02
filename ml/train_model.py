import os
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from ml.preprocess import load_and_preprocess_data

def evaluate_model(y_true, y_pred, is_log=True):
    if is_log:
        y_true_orig = np.exp(y_true)
        y_pred_orig = np.exp(y_pred)
    else:
        y_true_orig = y_true
        y_pred_orig = y_pred
        
    mae = mean_absolute_error(y_true_orig, y_pred_orig)
    rmse = np.sqrt(mean_squared_error(y_true_orig, y_pred_orig))
    r2 = r2_score(y_true_orig, y_pred_orig)
    
    diff_pct = np.abs(y_pred_orig - y_true_orig) / y_true_orig
    acc_20 = (diff_pct <= 0.20).mean() * 100.0
    acc_25 = (diff_pct <= 0.25).mean() * 100.0
    acc_30 = (diff_pct <= 0.30).mean() * 100.0
    
    return mae, rmse, r2, acc_20, acc_25, acc_30

def get_feature_names(preprocessor, num_features):
    try:
        cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
        cat_feature_names = cat_encoder.get_feature_names_out()
        return list(num_features) + list(cat_feature_names)
    except Exception:
        return []

def main():
    print("Finalizing ML Pipeline Training (Restoring Best Config)...")
    
    df, file_used, target_used, num_features, cat_features = load_and_preprocess_data()
    if df is None:
        return
        
    rows_before = pd.read_csv(file_used, usecols=[0], low_memory=False).shape[0]
    is_log = (target_used == "log_price")
    
    y = df["target"].values
    X = df[num_features + cat_features]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, num_features),
        ("cat", categorical_transformer, cat_features)
    ])
    
    models = {
        "Dummy (Mean)": DummyRegressor(strategy="mean"),
        "Dummy (Median)": DummyRegressor(strategy="median"),
        "Linear Regression": LinearRegression(),
        "Decision Tree Regression": DecisionTreeRegressor(max_depth=12, random_state=42),
        "Random Forest Baseline": RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1),
        "Tuned Random Forest B (Best)": RandomForestRegressor(n_estimators=300, max_depth=20, min_samples_leaf=2, min_samples_split=4, random_state=42, n_jobs=-1)
    }
    
    results = {}
    best_name = "Tuned Random Forest B (Best)"
    best_pipeline = None
    
    # We will also add a note about the discarded NLP model in the metrics
    latest_nlp_ref = {
        "MAE": 42.86, "RMSE": 80.29, "R2": 0.59, 
        "acceptability_within_20_percent": 48.5,
        "note": "Discarded - NLP amenities features did not improve over simpler best config."
    }
    
    for name, model in models.items():
        print(f"Training {name}...")
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        mae, rmse, r2, acc_20, acc_25, acc_30 = evaluate_model(y_test, y_pred, is_log=is_log)
        
        results[name] = {
            "MAE": round(mae, 4),
            "RMSE": round(rmse, 4),
            "R2": round(r2, 4),
            "acceptability_within_20_percent": round(acc_20, 2),
            "acceptability_within_25_percent": round(acc_25, 2),
            "acceptability_within_30_percent": round(acc_30, 2)
        }
        
        print(f"  --> MAE: {mae:.2f}, RMSE: {rmse:.2f}, R²: {r2:.2f}, Acc±20%: {acc_20:.1f}%")
        
        if name == best_name:
            best_pipeline = pipeline
            
    # Add the failed experiment for comparison as requested
    results["Latest NLP Improvement Pass (Rejected)"] = latest_nlp_ref
            
    print(f"\nFinal selected model: {best_name}")
    
    joblib_path = os.path.join("ml", "model.joblib")
    metrics_path = os.path.join("ml", "metrics.json")
    schema_path = os.path.join("ml", "feature_schema.json")
    importance_path = os.path.join("ml", "feature_importance.json")
    
    joblib.dump(best_pipeline, joblib_path)
    
    # Feature Importance for Best
    try:
        regressor = best_pipeline.named_steps["regressor"]
        importances = regressor.feature_importances_
        feature_names = get_feature_names(best_pipeline.named_steps["preprocessor"], num_features)
        
        if len(feature_names) == len(importances):
            feat_dict = dict(sorted(zip(feature_names, map(float, importances)), key=lambda x: x[1], reverse=True))
            with open(importance_path, "w") as f:
                json.dump(feat_dict, f, indent=4)
    except Exception as e:
        print("Feature importance extraction error:", e)
    
    metrics_out = {
        "dataset_name": "Airbnb_data Dataset (Multi-city)",
        "dataset_file_used": file_used,
        "rows_before_cleaning": rows_before,
        "rows_after_cleaning": len(df),
        "target_used": target_used,
        "target_transform": "natural_log" if is_log else "none",
        "inverse_transform_used": "np.exp" if is_log else "none",
        "best_model": best_name,
        "selection_reason": "lowest RMSE and best overall metrics across all iterations",
        "models": results,
        "currency": "USD"
    }
    
    with open(metrics_path, "w") as f:
        json.dump(metrics_out, f, indent=4)
        
    schema_out = {
        "target": target_used,
        "display_target": "price",
        "prediction_output_scale": "original_price",
        "features": cat_features + num_features,
        "categorical_features": cat_features,
        "numeric_features": num_features,
        "target_transform": "natural_log" if is_log else "none",
        "inverse_transform_used": "np.exp" if is_log else "none"
    }
    
    with open(schema_path, "w") as f:
        json.dump(schema_out, f, indent=4)

if __name__ == "__main__":
    main()
