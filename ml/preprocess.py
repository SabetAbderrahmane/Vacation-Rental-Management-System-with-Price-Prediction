import os
import pandas as pd
import numpy as np

def count_amenities(val):
    if pd.isna(val):
        return 0
    val_str = str(val).strip()
    if val_str.startswith("{") and val_str.endswith("}"):
        items = [i for i in val_str[1:-1].split(",") if i.strip()]
        return len(items)
    return len([i for i in val_str.split(",") if i.strip()])

def normalize_room_type(val):
    if pd.isna(val):
        return "Unknown"
    val = str(val).lower().strip()
    if "entire home" in val or "entire apt" in val:
        return "entire_home"
    if "private_room" in val or "private room" in val:
        return "private_room"
    if "shared room" in val:
        return "shared_room"
    if "hotel room" in val:
        return "hotel_room"
    return str(val)

def load_and_preprocess_data():
    dataset_paths = [
        os.path.join("ml", "dataset", "raw", "Airbnb_data.csv"),
        os.path.join("ml", "dataset", "raw", "listings.csv.gz"),
        os.path.join("ml", "dataset", "raw", "listings.csv")
    ]
    
    file_used = None
    for path in dataset_paths:
        if os.path.exists(path):
            file_used = path
            break
            
    if not file_used:
        print("Dataset file not found.")
        return None, None, None, None, None
        
    print(f"Dataset file used: {file_used}")
    df = pd.read_csv(file_used, low_memory=False)
    rows_before = len(df)
    print(f"Row count before cleaning: {rows_before}")
    
    # Target Detection
    if "price" in df.columns and pd.to_numeric(df["price"], errors="coerce").notna().sum() > 0:
        target_used = "price"
        df["target"] = pd.to_numeric(df["price"], errors="coerce")
    elif "log_price" in df.columns and pd.to_numeric(df["log_price"], errors="coerce").notna().sum() > 0:
        target_used = "log_price"
        df["target"] = pd.to_numeric(df["log_price"], errors="coerce")
    else:
        print("No usable target.")
        return None, None, None, None, None
        
    df = df.dropna(subset=["target"])
    
    # Feature Mapping (Reverted to best config version)
    num_map = [
        ("accommodates", "max_guests"),
        ("bathrooms", "bathrooms"),
        ("bedrooms", "bedrooms"),
        ("beds", "beds"),
        ("number_of_reviews", "number_of_reviews"),
        ("review_scores_rating", "review_score"),
        ("latitude", "latitude"),
        ("longitude", "longitude")
    ]
    
    cat_map = [
        ("city", "city"),
        ("neighbourhood", "location"),
        ("room_type", "room_type"),
        ("property_type", "property_type"),
        ("bed_type", "bed_type"),
        ("cancellation_policy", "cancellation_policy"),
        ("cleaning_fee", "cleaning_fee"),
        ("instant_bookable", "instant_bookable"),
        ("host_identity_verified", "host_identity_verified")
    ]
    
    selected_num = []
    for raw, norm in num_map:
        if raw in df.columns:
            df[norm] = pd.to_numeric(df[raw], errors="coerce")
            selected_num.append(norm)
            
    if "amenities" in df.columns:
        df["amenities_count"] = df["amenities"].apply(count_amenities)
        selected_num.append("amenities_count")
        
    selected_cat = []
    for raw, norm in cat_map:
        if raw in df.columns:
            if norm == "room_type":
                df[norm] = df[raw].apply(normalize_room_type)
            else:
                df[norm] = df[raw].astype(str).replace("nan", np.nan)
            selected_cat.append(norm)
            
    final_cols = ["target"] + selected_num + selected_cat
    df = df[final_cols].copy()
    
    # Cleaning
    p1 = df["target"].quantile(0.01)
    p99 = df["target"].quantile(0.99)
    df = df[(df["target"] >= p1) & (df["target"] <= p99)]
    df = df.drop_duplicates()
    
    print(f"Rows after cleaning: {len(df)}")
    return df, file_used, target_used, selected_num, selected_cat
