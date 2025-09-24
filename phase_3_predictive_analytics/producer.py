# producer.py
import pandas as pd
import time
import json
import logging
import sys
import random
from kafka import KafkaProducer
from kafka.errors import KafkaError

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("phase_3_predictive_analytics/logs/producer.log", mode="w")
    ]
)

TOPIC_NAME = "air_quality"
SLEEP_SECS = 1    # simulate delay between messages

# --- Kafka producer with retries ---
def create_producer():
    for attempt in range(5):
        try:
            producer = KafkaProducer(
                bootstrap_servers="localhost:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=3
            )
            logging.info("✅ Kafka producer created successfully")
            return producer
        except KafkaError as e:
            wait_time = 2 ** attempt + random.random()
            logging.error(f"❌ Failed to connect to Kafka (attempt {attempt+1}): {e}")
            logging.info(f"Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    sys.exit("Producer could not connect to Kafka after multiple attempts.")

producer = create_producer()

# --- Load and preprocess data ---
df = pd.read_csv("AirQualityData/AirQualityUCI.csv", sep=";")
df = df.dropna(axis=1, how="all")  # drop only fully empty cols
logging.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")

# --- Cleaning function ---
def clean_row(row):
    record = row.to_dict()

    # Preserve Date + Time as strings
    if "Date" in record and pd.notna(record["Date"]):
        record["Date"] = str(record["Date"]).strip()
    if "Time" in record and pd.notna(record["Time"]):
        record["Time"] = str(record["Time"]).strip()

    # Replace -200 with None
    record = {k: (None if v == -200 else v) for k, v in record.items()}

    # Drop junk rows
    if all(v is None or str(v).strip() == "" for v in record.values()):
        return None

    # Normalize numeric values
    for k, v in record.items():
        if k in ["Date", "Time"]:
            continue
        if isinstance(v, str):
            if "," in v:
                v = v.replace(",", ".")
            try:
                record[k] = float(v)
            except ValueError:
                record[k] = None

    # Basic range checks
    co_val = record.get("CO(GT)")
    if co_val is None or not (0 <= co_val <= 50):
        return None
    if record.get("NO2(GT)") is not None and not (0 <= record["NO2(GT)"] <= 1000):
        return None

    return record

# --- Stream one row at a time ---
start_time = time.time()
count, dropped = 0, 0

for _, row in df.iterrows():
    cleaned = clean_row(row)
    if not cleaned:
        dropped += 1
        continue

    try:
        producer.send(TOPIC_NAME, value=cleaned)
        count += 1
        logging.info(f"📤 Sent record #{count}: {cleaned}")
    except KafkaError as e:
        logging.error(f"Error sending record: {e}")

    time.sleep(SLEEP_SECS)

elapsed = time.time() - start_time
logging.info(
    f"✅ Completed sending {count} records in {elapsed:.2f}s "
    f"({count/elapsed:.2f} msg/sec). Dropped {dropped} invalid rows."
)
producer.flush()
