preprocessing_strategy.md
Dataset Overview

Source: UCI Air Quality Dataset (9,358 hourly sensor observations).

Challenges: Missing values encoded as -200, occasional junk rows (;;;;;;;;;;;;;;;).

Goal: Deliver cleaned, validated data suitable for real-time ingestion.

Hybrid Preprocessing Approach

We adopted a hybrid strategy, splitting responsibilities between producer and consumer.

Producer-Side Cleaning (before Kafka)

Why: Prevents bad data from polluting the stream.

Steps:

Convert -200 → None.

Drop rows with all missing values or invalid types.

Range validation:

CO(GT): 0–50 mg/m³

NOx(GT): 0–5000 ppb

NO2(GT): 0–1000 µg/m³

T: -50–60 °C

RH: 0–100 %

AH: ≥0

Impute missing temperature (T) with 0.

Result: 6,941 valid rows sent (≈2,530 dropped before send).

Consumer-Side Validation (after Kafka)

Why: Defense-in-depth + operational checks.

Steps:

Re-validate CO(GT) presence.

Enrich rows with NO2_status:

Unhealthy if NO₂ > 200 µg/m³.

OK otherwise.

Append valid batches to cleaned_air_quality.csv.

Monitoring: Logs batch size, throughput, dropped rows (after receiving), and unhealthy NO₂ counts.

Quality Metrics

Producer: Reports total rows scanned, valid vs dropped counts.

Consumer: Reports rows processed, unhealthy percentage, throughput.

Final Dataset: Cleaned CSV with headers, preserved Date + Time.

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025). Prompts and responses used are documented in Appendix A (appendix_ai_usage/appendix_kafka.txt).