# consumer.py
from kafka import KafkaConsumer
import json
import logging
import sys
import time
import pandas as pd
import os

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("phase_1_streaming_infrastructure/logs/consumer.log", mode="w")
    ]
)

TOPIC_NAME = "air_quality"
OUTPUT_FILE = "phase_1_streaming_infrastructure/cleaned_air_quality.csv"

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="air-quality-consumer",
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)

logging.info("✅ Consumer connected and waiting for messages...")

processed, dropped, unhealthy_no2 = 0, 0, 0
start_time = time.time()

# Reset output file
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

for msg in consumer:
    try:
        batch = msg.value
        if not isinstance(batch, list):
            continue

        valid_rows = []
        for event in batch:
            if event.get("CO(GT)") is None:
                dropped += 1
                continue

            if event.get("NO2(GT)") and event["NO2(GT)"] > 200:
                event["NO2_status"] = "Unhealthy"
                unhealthy_no2 += 1
            else:
                event["NO2_status"] = "OK"

            valid_rows.append(event)
            processed += 1

        # Write to CSV with headers preserved
        if valid_rows:
            df = pd.DataFrame(valid_rows)
            write_header = not os.path.exists(OUTPUT_FILE)
            df.to_csv(OUTPUT_FILE, mode="a", index=False, header=write_header)
            logging.info(f"💾 Wrote {len(valid_rows)} records to {OUTPUT_FILE}")

        if processed % 100 == 0:
            elapsed = time.time() - start_time
            logging.info(
                f"📊 Metrics: {processed} processed | {dropped} dropped after receiving | {unhealthy_no2} unhealthy NO2 "
                f"| {(processed/elapsed):.2f} msg/sec"
            )

    except Exception as e:
        logging.error(f"⚠️ Error processing batch: {e}")
