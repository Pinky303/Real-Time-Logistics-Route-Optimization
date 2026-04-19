# Data Dictionary

Comprehensive schema documentation for all data layers in the pipeline.

## Bronze Layer

### Kinesis GPS Stream (Raw Events)

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `device_id` | STRING | Unique device identifier | "DEV_12345" | No |
| `driver_id` | STRING | Driver identifier (links to lookup) | "485" | No |
| `latitude` | DOUBLE | GPS latitude coordinate | 30.0444 | No |
| `longitude` | DOUBLE | GPS longitude coordinate | 31.2357 | No |
| `gps_timestamp` | TIMESTAMP | Event timestamp from device | "2026-04-19 14:30:00" | No |
| `speed` | DOUBLE | Speed in km/h from GPS | 45.5 | Yes |
| `altitude` | DOUBLE | Altitude in meters | 25.0 | Yes |
| `route_id` | STRING | Route identifier | "ROUTE_001" | Yes |

### CSV Delivery Orders (Batch Historical Data)

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `Order_ID` | INTEGER | Unique order identifier | 12345 | No |
| `Driver_ID` | INTEGER | Driver identifier | 485 | No |
| `Driver_Lat` | DOUBLE | Driver latitude at delivery | 30.0444 | Yes |
| `Driver_Lon` | DOUBLE | Driver longitude at delivery | 31.2357 | Yes |
| `Delivery_Distance_km` | DOUBLE | Distance traveled in km | 15.3 | Yes |
| `Delivery_Duration_Minutes` | INTEGER | Time taken in minutes | 35 | Yes |
| `City` | STRING | Delivery city | "Cairo" | Yes |
| `Traffic_Level` | STRING | Traffic condition | "Heavy" | Yes |
| `Delivery_Time` | TIMESTAMP | Delivery completion time | "2026-04-19 14:30:00" | Yes |
| `Order_Status` | STRING | Order completion status | "Delivered" | Yes |
| `Customer_Rating` | INTEGER | Customer satisfaction (1-5) | 4 | Yes |
| `Delivery_Fee` | DOUBLE | Delivery charge | 5.50 | Yes |
| `Vehicle_Type` | STRING | Type of delivery vehicle | "Motorcycle" | Yes |
| `Weather_Conditions` | STRING | Weather at delivery time | "Clear" | Yes |
| `Peak_Hour` | BOOLEAN | Delivered during peak hours | true | Yes |

## Silver Layer

### Enriched Delivery Data

Result of joining Bronze data with Driver Lookup table and calculating derived metrics.

| Column | Data Type | Description | Example | Nullable | Source |
|--------|-----------|-------------|---------|----------|--------|
| `order_id` | INTEGER | Unique order identifier | 12345 | No | Bronze |
| `driver_id` | INTEGER | Driver identifier | 485 | No | Bronze |
| `driver_name` | STRING | Driver full name | "Ahmed Khan" | Yes | Lookup Join |
| `route_city` | STRING | Delivery city | "Cairo" | Yes | Bronze |
| `latitude` | DOUBLE | GPS latitude | 30.0444 | Yes | Bronze |
| `longitude` | DOUBLE | GPS longitude | 31.2357 | Yes | Bronze |
| `delivery_timestamp` | TIMESTAMP | Delivery time | "2026-04-19 14:30:00" | Yes | Bronze |
| `actual_speed_kmh` | DOUBLE | Calculated actual speed | 26.2 | Yes | **Calculated** |
| `expected_speed_kmh` | DOUBLE | Expected speed for driver | 50.0 | Yes | Lookup Join |
| `delivery_duration_min` | INTEGER | Actual delivery duration | 35 | Yes | Bronze |
| `expected_duration_baseline` | INTEGER | Expected duration | 30 | Yes | Lookup Join |
| `distance_km` | DOUBLE | Delivery distance | 15.3 | Yes | Bronze |
| `traffic_level` | STRING | Traffic condition | "Heavy" | Yes | Bronze |
| `order_status` | STRING | Order status | "Delivered" | Yes | Bronze |
| `processing_time` | TIMESTAMP | Pipeline processing time | "2026-04-19 14:35:00" | No | **System** |
| `speed_deviation` | DOUBLE | Actual - expected speed | -23.8 | Yes | **Calculated** |
| `duration_deviation` | INTEGER | Actual - expected duration | 5 | Yes | **Calculated** |
| `is_delayed` | BOOLEAN | Delay flag (< 85% expected) | true | Yes | **Calculated** |

### Calculated Formulas

```python
# Actual Speed (km/h)
actual_speed_kmh = distance_km / (delivery_duration_min / 60.0)

# Speed Deviation (km/h)
speed_deviation = actual_speed_kmh - expected_speed_kmh

# Duration Deviation (minutes)
duration_deviation = delivery_duration_min - expected_duration_baseline

# Delay Flag
is_delayed = actual_speed_kmh < (expected_speed_kmh * 0.85)
```

## Gold Layer

### Route Performance Metrics

Aggregated performance by city/route.

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `route_city` | STRING | City name | "Cairo" | No |
| `total_deliveries` | LONG | Total delivery count | 12,500 | No |
| `unique_drivers` | LONG | Number of distinct drivers | 8 | No |
| `avg_speed_kmh` | DOUBLE | Average actual speed | 35.2 | Yes |
| `expected_speed_kmh` | DOUBLE | Average expected speed | 50.0 | Yes |
| `avg_speed_deviation` | DOUBLE | Average deviation | -14.8 | Yes |
| `delayed_deliveries` | LONG | Count of delayed deliveries | 10,234 | No |
| `delay_percentage` | DOUBLE | Percentage of delays | 81.87 | Yes |

### Delayed Driver Analysis

Driver-level performance metrics.

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `driver_id` | INTEGER | Driver identifier | 485 | No |
| `driver_name` | STRING | Driver full name | "Ahmed Khan" | Yes |
| `route_city` | STRING | City/route name | "Cairo" | Yes |
| `total_deliveries` | LONG | Total deliveries by driver | 280 | No |
| `avg_actual_speed` | DOUBLE | Average actual speed | 4.30 | Yes |
| `avg_expected_speed` | DOUBLE | Average expected speed | 50.0 | Yes |
| `avg_speed_deviation` | DOUBLE | Average deviation | -45.70 | Yes |
| `delayed_deliveries` | LONG | Count of delayed deliveries | 280 | No |
| `delay_rate_percentage` | DOUBLE | Percentage of delays | 100.0 | Yes |

### Optimization Recommendations

Driver reassignment suggestions.

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `route_city` | STRING | City name | "Cairo" | No |
| `current_driver_id` | INTEGER | Underperforming driver ID | 364 | Yes |
| `current_driver_name` | STRING | Underperforming driver name | "Omar Abdullah" | Yes |
| `current_delay_rate` | DOUBLE | Current delay rate % | 100.0 | Yes |
| `replacement_driver_id` | INTEGER | Best performer driver ID | 32 | Yes |
| `replacement_driver_name` | STRING | Best performer name | "Fatima Hassan" | Yes |
| `replacement_delay_rate` | DOUBLE | Best performer delay rate | 100.0 | Yes |
| `potential_improvement_percent` | DOUBLE | Expected improvement | 0.0 | Yes |

## Lookup Tables

### Driver Lookup

Static reference data for driver expected performance.

| Column | Data Type | Description | Example | Nullable |
|--------|-----------|-------------|---------|----------|
| `driver_id` | INTEGER | Unique driver identifier | 485 | No |
| `driver_name` | STRING | Driver full name | "Ahmed Khan" | No |
| `city` | STRING | Primary city assignment | "Cairo" | No |
| `expected_speed_kmh` | DOUBLE | Baseline expected speed | 50.0 | No |
| `expected_duration_baseline` | INTEGER | Baseline expected duration (min) | 30 | No |

## Data Quality Rules

### Validation Checks

1. **Speed Validity**
   - Condition: `0 < actual_speed_kmh < 150`
   - Action: Filter out invalid records

2. **Coordinate Validity**
   - Condition: `latitude IS NOT NULL AND longitude IS NOT NULL`
   - Action: Filter out records without coordinates

3. **Minimum Deliveries**
   - Condition: `COUNT(deliveries) >= 3` (Gold layer)
   - Action: Exclude drivers with insufficient data

4. **Timestamp Validity**
   - Condition: `delivery_timestamp IS NOT NULL`
   - Action: Filter out records without timestamps

## Data Lineage

```
Kinesis/CSV (Bronze)
  ↓
  │─── JOIN → driver_lookup.csv
  │─── CALCULATE → actual_speed_kmh
  │─── CALCULATE → speed_deviation
  │─── CALCULATE → is_delayed
  │─── FILTER → data quality rules
  ↓
Silver (Enriched)
  ↓
  │─── GROUP BY → route_city
  │─── GROUP BY → driver_id, route_city
  │─── WINDOW → ranking functions
  ↓
Gold (Aggregated)
  ↓
  │─── Dashboards
  │─── Alerts
  │─── ML Models
```

## Partitioning Strategy

### Silver Layer
- **Partition Column**: `route_city`
- **Reason**: Most queries filter by city
- **Cardinality**: ~8 cities (low, manageable)
- **Benefit**: Partition pruning for city-specific queries

### Example Query with Partition Pruning
```sql
SELECT * FROM silver_enriched 
WHERE route_city = 'Cairo'
-- Only reads Cairo partition, skipping other cities
```

## Data Types Reference

| SQL Type | Python Type | Spark Type | Description |
|----------|-------------|------------|-------------|
| INTEGER | int | IntegerType | 32-bit signed integer |
| LONG | int | LongType | 64-bit signed integer |
| DOUBLE | float | DoubleType | Double precision float |
| STRING | str | StringType | UTF-8 encoded string |
| BOOLEAN | bool | BooleanType | True/False value |
| TIMESTAMP | datetime | TimestampType | Date and time with timezone |

## Sample Data

### Bronze CSV Sample
```csv
Order_ID,Driver_ID,Driver_Lat,Driver_Lon,Delivery_Distance_km,Delivery_Duration_Minutes,City
12345,485,30.0444,31.2357,15.3,35,Cairo
12346,65,31.2001,29.9187,8.2,45,Alexandria
```

### Silver Enriched Sample
```csv
order_id,driver_id,driver_name,route_city,actual_speed_kmh,expected_speed_kmh,speed_deviation,is_delayed
12345,485,"Ahmed Khan",Cairo,26.2,50.0,-23.8,true
12346,65,"Sarah Ali",Alexandria,10.9,50.0,-39.1,true
```

### Gold Route Performance Sample
```csv
route_city,total_deliveries,avg_speed_kmh,delay_percentage
Cairo,12500,35.2,81.87
Alexandria,12476,35.2,82.26
```

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-04-19 | Initial schema | Pinky Somwani |
| 1.1 | TBD | Add ML prediction columns | TBD |

## Glossary

* **Delay**: Delivery where actual speed < 85% of expected speed
* **Speed Deviation**: Difference between actual and expected speed (km/h)
* **Duration Deviation**: Difference between actual and expected duration (minutes)
* **Route**: Geographic area or city where deliveries occur
* **Expected Speed**: Baseline performance metric from driver lookup table
* **Delay Rate**: Percentage of deliveries flagged as delayed