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
        logging.FileHandler("phase_1_streaming_infrastructure/logs/producer.log", mode="w")
    ]
)

TOPIC_NAME = "air_quality"
BATCH_SIZE = 50   # send 50 rows at a time
SLEEP_SECS = 1    # simulate delay between batches

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

# --- Hybrid cleaning & validation function ---
'''
Part of the cleaning logic is inspired by discussions with ChatGPT 
on what current practices are when it comes to data cleaning and validation 
in air quality sensor data. Utilized https://archive.ics.uci.edu/dataset/360/air+quality
website given in the project description for domain knowledge as well.
'''
def clean_row(row):
    record = row.to_dict()

    # Preserve Date + Time as strings
    if "Date" in record and pd.notna(record["Date"]):
        record["Date"] = str(record["Date"]).strip()
    if "Time" in record and pd.notna(record["Time"]):
        record["Time"] = str(record["Time"]).strip()

    # Replace -200 with None
    record = {k: (None if v == -200 else v) for k, v in record.items()}

    # Drop junk rows (all empty or NaN)
    if all(v is None or str(v).strip() == "" for v in record.values()):
        return None

    # Normalize numeric values (ignore Date/Time)
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

    # Required field: CO(GT)
    co_val = record.get("CO(GT)")
    if co_val is None:
        return None

    # Range checks
    def in_range(val, low, high):
        return isinstance(val, (int, float)) and low <= val <= high

    if not in_range(co_val, 0, 50):
        return None
    if not in_range(record.get("NOx(GT)"), 0, 5000):
        return None
    if not in_range(record.get("NO2(GT)"), 0, 1000):
        return None
    if not in_range(record.get("T"), -50, 60):
        return None
    if not in_range(record.get("RH"), 0, 100):
        return None
    if record.get("AH") is not None and record["AH"] < 0:
        return None

    # Impute missing T with 0
    if record.get("T") is None:
        record["T"] = 0

    return record

# --- Stream in batches ---
start_time = time.time()
count, dropped = 0, 0
batch = []

for _, row in df.iterrows():
    cleaned = clean_row(row)
    if cleaned:
        batch.append(cleaned)
    else:
        dropped += 1

    if len(batch) >= BATCH_SIZE:
        try:
            producer.send(TOPIC_NAME, value=batch)
            count += len(batch)
            logging.info(f"📤 Sent batch of {len(batch)} records. Total sent={count}")
            batch = []
        except KafkaError as e:
            logging.error(f"Error sending batch: {e}")

        time.sleep(SLEEP_SECS)

# send leftovers
if batch:
    producer.send(TOPIC_NAME, value=batch)
    count += len(batch)
    logging.info(f"📤 Sent final batch of {len(batch)} records. Total sent={count}")

elapsed = time.time() - start_time
logging.info(
    f"✅ Completed sending {count} records in {elapsed:.2f}s "
    f"({count/elapsed:.2f} msg/sec). Dropped {dropped} invalid rows before sending to consumer."
)
producer.flush()
