from kafka import KafkaConsumer
import json, joblib, pandas as pd
import sys, os
from src.data_preprocessing import prepare_features


# Import same preprocessing
# sys.path.append(os.path.abspath("../src"))
# from data_preprocessing import prepare_features

# Load model

BASE_DIR = os.path.dirname(__file__)
model_path = os.path.join(BASE_DIR, "models", "xgboost_no2_model.pkl")
model = joblib.load(model_path)


# Start consumer
consumer = KafkaConsumer(
    'air_quality',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset="earliest",   # <-- important
    enable_auto_commit=True,
    group_id="air_quality_group"    # add a group_id to persist offsets
)


print("Consumer started, waiting for messages...")

for msg in consumer:
    data = msg.value
    df = pd.DataFrame([data])  
    
    # Transform
    X = prepare_features(df)
    
    # Predict
    pred = model.predict(X)[0]
    
    print(f"Timestamp: {data['timestamp']} | Actual: {data.get('NO2(GT)')} | Predicted: {pred:.2f}")
