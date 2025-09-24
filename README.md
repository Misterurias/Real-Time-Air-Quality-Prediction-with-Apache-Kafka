# Real-Time Air Quality Prediction with Apache Kafka

## 📌 Project Overview
This project implements a **real-time streaming analytics pipeline** for predicting air quality using **Apache Kafka** and machine learning.  
It was developed as part of the *Fundamentals of Operationalizing AI* course, with the goal of demonstrating how to operationalize AI models in a streaming environment for actionable environmental insights.

The pipeline ingests simulated IoT sensor data, processes it through Kafka topics, and performs real-time predictions using multiple machine learning models.  
Key deliverables included infrastructure setup, data intelligence analysis, model development, and deployment.

---

## 🎯 Objectives
- Build a **Kafka-based streaming infrastructure** for environmental data.  
- Ingest, transform, and analyze **air quality sensor streams** in real-time.  
- Develop **predictive models** (regression, ensembles, time series, deep learning).  
- Deploy models for real-time inference on streaming data.  
- Provide insights for **policy makers, communities, and environmental stakeholders**.

---

## ⚙️ Technical Architecture
The project follows a modular architecture:

1. **Data Ingestion (Phase 1)**  
   - Simulated IoT air quality sensors streaming data into **Kafka Producers**.  
   - Kafka topics used for ingestion: `air_quality_raw`.  

2. **Streaming Infrastructure**  
   - **Apache Kafka + Zookeeper** for distributed messaging.  
   - Kafka **Consumers** to read and process sensor data in real-time.  

3. **Data Intelligence & Analysis (Phase 2)**  
   - Exploratory Data Analysis (EDA) on historical datasets.  
   - Feature engineering (temporal features, lag values, rolling averages).  
   - Business insights: temporal patterns, pollutant correlations, seasonal/diurnal cycles.  

4. **Predictive Analytics (Phase 3)**  
   Implemented multiple models for air quality forecasting:  
   - **XGBoost** for gradient boosting.  
   - **SARIMA** time series forecasting.  

   Confidence intervals and evaluation metrics (RMSE, MAE, R²) were calculated for performance comparison.

5. **Deployment (Phase 3 & 4)**  
   - Real-time inference service (`consumer.py`) consuming from Kafka topics.  
   - Predictions pushed to `air_quality_predictions` Kafka topic.  
   - Monitoring for **system performance & model drift**.  

---

## 📊 Key Findings & Insights
- **Pollutant correlations**: PM2.5 levels strongly correlated with PM10 and NO2.  
- **Temporal patterns**: Daily and weekly cycles, with higher pollution during traffic rush hours.  
- **Model performance**:  
  - XGBoost consistently outperformed SARIMA model.  
  - Confidence intervals revealed uncertainty bounds useful for decision-making.  

**Business Value:**  
- Real-time predictions enable **early warnings** for hazardous air conditions.  
- Provides **data-driven insights** for traffic regulation, industrial activity monitoring, and public health advisories.  
