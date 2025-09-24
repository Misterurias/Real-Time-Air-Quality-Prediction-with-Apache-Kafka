# Phase 3: Predictive Analytics Model Development and Deployment

## Strategic Objective
To develop, validate, and deploy machine learning models for real-time air quality forecasting, integrating streaming data with predictive analytics for operational decision-making.


## Model Development Framework

### Implemented Models
- **Foundation Models**:
  - Linear Regression
  - Random Forest
  - XGBoost (final selected model)
- **Advanced Model (Bonus)**:
  - SARIMA (explored as comparison)

### Feature Engineering
- Temporal features: hour, day, month, weekend indicator
- Cyclical encoding: sine/cosine transforms for hour and month
- Lagged features and rolling statistics were included in initial experiments but removed for real-time deployment compatibility

### Validation
- Chronological train/test split (70/30)
- Metrics:  
  - **Baseline (naïve previous value):** MAE = 13.08, RMSE = 16.79  
  - **XGBoost:** MAE = 6.42, RMSE = 8.32  
- Confidence intervals were computed using bootstrapped residuals


## Production Integration and Deployment

### Architecture
Data Source → Kafka Producer → Kafka Topic (air_quality) → Kafka Consumer → Model Inference → Predictions


- **Producer:** Streams cleaned rows from the UCI Air Quality dataset into Kafka topic `air_quality`.
- **Consumer:** Subscribes to `air_quality`, applies consistent feature engineering, loads XGBoost model, and outputs real-time predictions.

### Operational Documentation
- **Logs:** Producer logs batches sent, consumer logs predictions
- **Monitoring:** Future enhancements could include:
  - Drift detection by comparing rolling MAE/RMSE to validation benchmarks
  - Alerting if prediction errors exceed thresholds
- **Resilience:** Kafka’s retry and partitioning provide fault tolerance


## Performance Assessment

- **XGBoost significantly outperformed the naïve baseline** (RMSE 8.32 vs. 16.79).
- The deployed pipeline demonstrates:
  - Low-latency predictions
  - Compatibility with real-time streaming
  - Clear performance improvement over baseline


## Conclusion

Phase 3 successfully demonstrates the full operationalization of predictive analytics:
- Model training and evaluation
- Real-time Kafka integration
- Streaming inference with reproducible setup
- Deployment-ready documentation

The framework provides a foundation for scaling to other pollutants and datasets, with monitoring and retraining for long-term deployment.

## Academic Integrity Note

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025).  
Prompts and responses are documented in **Appendix A** (`appendix_ai_usage/appendix_phase3_model_development.txt`) and (`appendix_ai_usage/appendix_deployment_section_steps.txt`).