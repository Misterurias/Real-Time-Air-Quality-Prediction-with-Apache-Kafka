setup_and_architecture.md
Kafka Setup and Configuration

Version: Apache Kafka 3.9.1 (last release with ZooKeeper).

ZooKeeper: Required for broker coordination. Launched via bin/zookeeper-server-start.sh config/zookeeper.properties.

Broker: Started with bin/kafka-server-start.sh config/server.properties.

Topic: Created air_quality with 1 partition and replication factor 1 (sufficient for local development).

bin/kafka-topics.sh --create \
  --topic air_quality \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

Architecture Decisions

Local Deployment: Chosen for simplicity and grading — no containerization or cluster needed.

ZooKeeper: Even though ZooKeeper is being phased out, this assignment requires learning fundamentals, so 3.9.1 ensures compatibility.

Single Partition: Our dataset is relatively small and the goal is correctness, not horizontal scaling. A single partition avoids offset management complexity.

File-Based Logs: Both producer and consumer log to logs/ for transparency and monitoring.

Error Handling and Resilience

Producer: Retry logic with exponential backoff (up to 5 attempts).

Consumer: Graceful error logging per batch, no crash on malformed data.

Monitoring: Metrics are logged every 100 rows for throughput, drops, and unhealthy NO₂ counts.

This assignment was completed with the use of generative AI (OpenAI ChatGPT, GPT-5, September 2025). Prompts and responses used are documented in Appendix A (appendix_ai_usage/appendix_kafka.txt).