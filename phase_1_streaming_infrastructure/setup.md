# Kafka Setup and Configuration

**Version:** Apache Kafka 3.9.1 (latest release with ZooKeeper)  

---

## Components

- **ZooKeeper**: Required for broker coordination.  
  - Launched via:  
    ```bash
    bin/zookeeper-server-start.sh config/zookeeper.properties
    ```

- **Broker**: Started with:  
    ```bash
    bin/kafka-server-start.sh config/server.properties
    ```

- **Topic**: Created `air_quality` with 1 partition and replication factor 1 (sufficient for local development).  
    ```bash
    bin/kafka-topics.sh --create \
      --topic air_quality \
      --bootstrap-server localhost:9092 \
      --partitions 1 \
      --replication-factor 1
    ```

---

## Architecture Decisions

- **Local Deployment**: Chosen for simplicity and grading — no containerization or cluster needed.  
- **ZooKeeper**: Still used despite deprecation to ensure compatibility for this assignment.  
- **Single Partition**: Dataset is relatively small; 1 partition avoids offset complexity.  
- **File-Based Logs**: Both producer and consumer log to files for transparency and monitoring.  

---

## Error Handling and Resilience

- **Producer**: Retry logic with exponential backoff (up to 5 attempts).  
- **Consumer**: Graceful error logging per batch, no crash on malformed data.  

---

## Monitoring

- Metrics logged every 100 rows:  
  - Throughput  
  - Dropped rows  
  - Unhealthy NO₂ counts  

---

## Academic Integrity Note

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025).  
Prompts and responses are documented in **Appendix A** (`appendix_ai_usage/appendix_kafka.txt`).
