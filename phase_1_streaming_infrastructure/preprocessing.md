# Preprocessing Strategy

## Dataset Overview

- **Source**: UCI Air Quality Dataset (9,358 hourly sensor observations)  
- **Challenges**:  
  - Missing values encoded as `-200`  
  - Occasional junk rows (`;;;;;;;;;;;;;;;`)  

- **Goal**: Deliver cleaned, validated data suitable for real-time ingestion  


## Hybrid Preprocessing Approach

We split responsibilities between **producer-side cleaning** (before Kafka) and **consumer-side validation** (after Kafka).  


### Producer-Side Cleaning

**Why:** Prevents invalid data from polluting the stream  

**Steps:**  
1. Convert `-200 → None`  
2. Drop rows with all missing values or invalid types  
3. Normalize numeric formats (commas → dots, type coercion)  
4. Range validation:  

| Feature   | Valid Range     | Unit |
|-----------|----------------|------|
| CO(GT)    | 0–50           | mg/m³ |
| NOx(GT)   | 0–5000         | ppb |
| NO2(GT)   | 0–1000         | µg/m³ |
| T         | -50–60         | °C |
| RH        | 0–100          | % |
| AH        | ≥ 0            | – |

5. Impute missing `T` with `0`  

**Result:**  
- 6,941 valid rows sent  
- 2,530 dropped (≈27%)  


### Consumer-Side Validation

**Why:** Defense-in-depth + operational checks  

**Steps:**  
1. Re-validate `CO(GT)` presence  
2. Add **NO₂ status flag**:  
   - `Unhealthy` if NO₂ > 200 µg/m³  
   - `OK` otherwise  
3. Append valid batches to `cleaned_air_quality.csv`  

---

## Monitoring & Metrics

- **Producer**: Logs valid rows sent vs. dropped  
- **Consumer**: Logs processed rows, unhealthy counts, throughput  


## Final Dataset

- Cleaned CSV with headers  
- Includes **Date** + **Time** columns  


## Academic Integrity Note

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025).  
Prompts and responses are documented in **Appendix A** (`appendix_ai_usage/appendix_kafka.txt`).
