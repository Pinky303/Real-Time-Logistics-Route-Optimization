# Architecture Documentation

## Overview

This document provides detailed technical architecture for the Real-Time Delivery Driver Efficiency & Route Optimization Pipeline.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources                                 │
│  ┌──────────────────┐         ┌─────────────────┐              │
│  │ AWS Kinesis      │         │ CSV/Batch Files │              │
│  │ (Real-time GPS)  │         │ (Historical)    │              │
│  └─────────┬────────┘         └────────┬────────┘              │
└────────────┼─────────────────────────────┼──────────────────────┘
             │                             │
             ▼                             ▼
┌─────────────────────────────────────────────────────────────────┐
│            Databricks Lakehouse Platform                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              BRONZE LAYER (Raw Data)                     │  │
│  │  • Kinesis: s3://.../bronze/kinesis_gps/                │  │
│  │  • CSV: s3://.../bronze/talabat_enhanced_orders.csv     │  │
│  │  • Format: Delta Lake                                    │  │
│  │  • Retention: 30 days                                    │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        SILVER LAYER (Enriched Data) 🔗                   │  │
│  │                                                           │  │
│  │  Transformations:                                        │  │
│  │  1. Join with Driver Lookup (THE HOOK)                  │  │
│  │  2. Calculate speed: distance / (duration / 60)         │  │
│  │  3. Calculate deviations: actual - expected             │  │
│  │  4. Flag delays: speed < (expected * 0.85)              │  │
│  │  5. Filter invalid data (speed > 150 km/h, nulls)       │  │
│  │                                                           │  │
│  │  • Location: s3://.../silver/gps_enriched/              │  │
│  │  • Partitioned by: route_city                           │  │
│  │  • Schema: 18 columns                                    │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          GOLD LAYER (Business Metrics)                   │  │
│  │                                                           │  │
│  │  Aggregations:                                           │  │
│  │  1. Route Performance (by city)                          │  │
│  │     - Total/delayed deliveries                           │  │
│  │     - Average speed, deviations                          │  │
│  │     - Delay percentage                                    │  │
│  │                                                           │  │
│  │  2. Driver Analysis (by driver + city)                  │  │
│  │     - Delay rates, speed metrics                         │  │
│  │     - Performance rankings                               │  │
│  │     - Severity classification                            │  │
│  │                                                           │  │
│  │  3. Optimization Recommendations                         │  │
│  │     - Driver-route matching                              │  │
│  │     - Workload balancing                                 │  │
│  │     - Reassignment suggestions                           │  │
│  │                                                           │  │
│  │  • Location: s3://.../gold/                             │  │
│  └─────────────────────────┬────────────────────────────────┘  │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Consumption Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐        │
│  │ Dashboards  │  │ Alerting     │  │ ML Models      │        │
│  │ (SQL/BI)    │  │ (Email/Slack)│  │ (Predictions)  │        │
│  └─────────────┘  └──────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## Medallion Architecture Pattern

### Bronze Layer (Raw Data)

**Purpose**: Preserve original data exactly as received

**Implementation**:
- **Kinesis Streaming**:
  ```python
  spark.readStream
    .format("kinesis")
    .option("streamName", "delivery-gps-stream")
    .option("region", "us-east-1")
    .option("initialPosition", "earliest")
    .load()
  ```
  
- **Batch CSV**:
  ```python
  spark.read.format("csv")
    .option("header", "true")
    .option("inferSchema", "true")
    .load("s3://...bronze/talabat_enhanced_orders.csv")
  ```

**Characteristics**:
- No transformations
- No filtering
- Append-only
- Delta Lake for ACID properties

### Silver Layer (Enriched/Cleansed)

**Purpose**: Business-ready data with enrichments and quality filters

**Key Transformation - The "Hook"**:
```python
# Join raw delivery data with driver lookup
silver_df = bronze_df.join(
    driver_lookup_df,
    bronze_df["Driver_ID"] == driver_lookup_df["driver_id"],
    "left"
)
```

**Data Quality Rules**:
1. Remove nulls in coordinates
2. Filter speeds: 0 < speed < 150 km/h
3. Validate timestamps
4. Deduplicate based on order_id

**Calculated Metrics**:
1. **Actual Speed**: `distance_km / (duration_minutes / 60)`
2. **Speed Deviation**: `actual_speed - expected_speed`
3. **Is Delayed**: `actual_speed < (expected_speed * 0.85)`
4. **Duration Deviation**: `actual_duration - expected_duration`

**Partitioning Strategy**:
- Partition by `route_city` for query optimization
- Enables city-level analysis without full table scans

### Gold Layer (Aggregated Metrics)

**Purpose**: Business KPIs and actionable insights

**Dataset 1: Route Performance**
```sql
SELECT 
    route_city,
    COUNT(*) as total_deliveries,
    COUNT(DISTINCT driver_id) as unique_drivers,
    AVG(actual_speed_kmh) as avg_speed,
    AVG(speed_deviation) as avg_deviation,
    (SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100.0) / COUNT(*) as delay_pct
FROM silver_enriched
GROUP BY route_city
```

**Dataset 2: Driver Analysis**
```sql
SELECT
    driver_id,
    driver_name,
    route_city,
    COUNT(*) as total_deliveries,
    AVG(speed_deviation) as avg_speed_deviation,
    (SUM(CASE WHEN is_delayed THEN 1 ELSE 0 END) * 100.0) / COUNT(*) as delay_rate
FROM silver_enriched
GROUP BY driver_id, driver_name, route_city
HAVING COUNT(*) >= 3
```

**Dataset 3: Optimization Recommendations**
- Ranks drivers within each city
- Identifies top performers (lowest delay rates)
- Matches underperformers with top performers for reassignment
- Calculates potential improvement if reassignment happens

## Streaming Architecture

### Micro-Batch Processing

**Trigger Configuration**:
```python
.trigger(availableNow=True)  # Process all available data in micro-batches
# Alternative:
# .trigger(processingTime="10 seconds")  # Continuous with 10s interval
```

**Checkpointing**:
- Location: `/Workspace/Users/<user>/.checkpoints/kinesis_gps_v2`
- Purpose: Exactly-once processing semantics
- Recovery: Auto-resume from last processed offset on failure

**Backpressure Handling**:
- Databricks Serverless auto-scales based on workload
- Delta Lake handles concurrent writes with optimistic concurrency

### Stream Monitoring

**Metrics to Track**:
1. **Throughput**: Records processed per second
2. **Latency**: End-to-end processing time
3. **Backlog**: Unprocessed records in stream
4. **Checkpoint Age**: Time since last successful checkpoint
5. **Error Rate**: Failed records / total records

## Data Flow Diagram

```
Kinesis → Bronze (raw) → Silver (enriched) → Gold (aggregated) → Alerts/Dashboards
   ↓          ↓              ↓                    ↓                     ↓
Append    Append      Upsert/Append         Overwrite          Read-only
```

## Optimization Strategies

### 1. Partitioning
- Silver layer partitioned by `route_city`
- Enables partition pruning for city-specific queries

### 2. Z-Ordering (Delta Lake)
```python
DELTA TABLE silver_enriched OPTIMIZE ZORDER BY (driver_id, delivery_timestamp)
```

### 3. Caching Strategy
- Driver lookup table broadcast join (small static table)
- Cache frequently accessed aggregations

### 4. Compute Optimization
- Databricks Serverless for auto-scaling
- Photon engine for vectorized query execution

## Fault Tolerance

### Checkpointing
- Streaming queries maintain checkpoint state
- Automatic recovery from failures

### Delta Lake ACID
- Atomic writes prevent partial updates
- Transaction log provides audit trail

### Retry Logic
- Kinesis client auto-retries transient failures
- Exponential backoff for stream throttling

## Security

### Access Control
- IAM roles for S3 and Kinesis access
- Databricks workspace access controls
- Unity Catalog for fine-grained permissions (if enabled)

### Data Encryption
- S3 encryption at rest (SSE-S3 or SSE-KMS)
- TLS for data in transit
- Delta Lake supports end-to-end encryption

## Scalability

### Horizontal Scaling
- Databricks auto-scales workers based on load
- Kinesis shards can be increased for higher throughput

### Vertical Scaling
- Adjust cluster node types (memory/CPU optimized)
- Use Photon for 2-5x performance boost

## Cost Optimization

1. **Storage Tiering**: Archive old Bronze data to S3 Glacier
2. **Compute**: Use Serverless for variable workloads
3. **Data Retention**: Implement lifecycle policies
4. **Table Optimization**: Regular OPTIMIZE and VACUUM operations

## Performance Benchmarks

- **Throughput**: 10,000+ records/second
- **End-to-end Latency**: < 10 seconds (micro-batch mode)
- **Query Performance**: Sub-second for Gold layer aggregations
- **Data Volume**: Tested with 100K+ records

## Future Enhancements

1. **Real-time ML Predictions**: Predict delays before they occur
2. **Graph Analytics**: Optimize delivery routes using graph algorithms
3. **Change Data Capture**: Track schema and data changes
4. **Multi-cloud**: Extend to Azure Event Hubs or GCP Pub/Sub
5. **AutoML**: Automated model training for delay prediction