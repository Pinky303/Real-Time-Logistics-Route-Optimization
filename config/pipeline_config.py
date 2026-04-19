"""
Pipeline Configuration

Centralized configuration for the delivery driver streaming pipeline.
Update these settings based on your environment (AWS region, S3 paths, etc.).
"""

# AWS Configuration
AWS_REGION = 'us-east-1'
KINESIS_STREAM_NAME = 'delivery-gps-stream'
KINESIS_ENDPOINT = f'https://kinesis.{AWS_REGION}.amazonaws.com'

# S3 Storage Paths
S3_BUCKET = 'amzn-s3-delivery-tracking'
BRONZE_PATH = f's3://{S3_BUCKET}/bronze/'
SILVER_PATH = f's3://{S3_BUCKET}/silver/'
GOLD_PATH = f's3://{S3_BUCKET}/gold/'

# Specific layer paths
BRONZE_KINESIS_PATH = f'{BRONZE_PATH}kinesis_gps/'
BRONZE_CSV_PATH = f'{BRONZE_PATH}talabat_enhanced_orders.csv'
SILVER_ENRICHED_PATH = f'{SILVER_PATH}gps_enriched/'
SILVER_CSV_ENRICHED_PATH = f'{SILVER_PATH}csv_enriched/'
GOLD_ROUTE_PERFORMANCE_PATH = f'{GOLD_PATH}route_performance/'
GOLD_DELAYED_DRIVERS_PATH = f'{GOLD_PATH}delayed_drivers/'
GOLD_STREAMING_SIMULATION_PATH = f'{GOLD_PATH}streaming_simulation/'

# Checkpoint Locations (Databricks Workspace paths)
CHECKPOINT_BASE_PATH = '/Workspace/Users/pinky.somwani.cs17@ggits.net/.checkpoints/'
KINESIS_CHECKPOINT = f'{CHECKPOINT_BASE_PATH}kinesis_gps_v2'
SILVER_CHECKPOINT = f'{CHECKPOINT_BASE_PATH}silver_enriched'
CSV_STREAM_CHECKPOINT = f'{CHECKPOINT_BASE_PATH}csv_stream_simulation'

# Streaming Configuration
STREAMING_CONFIG = {
    'kinesis': {
        'stream_name': KINESIS_STREAM_NAME,
        'region': AWS_REGION,
        'initial_position': 'earliest',  # 'earliest' or 'latest'
        'endpoint_url': KINESIS_ENDPOINT,
    },
    'trigger': {
        'mode': 'availableNow',  # Process all available data in micro-batches
        # Alternative: {'processingTime': '10 seconds'} for continuous processing
    },
    'output_mode': 'append',  # 'append', 'complete', or 'update'
}

# Business Logic Configuration
BUSINESS_RULES = {
    'delay_threshold': 0.85,  # Flag as delayed if speed < 85% of expected
    'alert_threshold_kmh': 10,  # Trigger alert if >10 km/h below expected
    'critical_threshold_kmh': 30,  # Critical alert threshold
    'high_threshold_kmh': 20,  # High severity threshold
    'min_deliveries_for_analysis': 3,  # Minimum deliveries to include driver in analysis
    'delay_rate_intervention_threshold': 50,  # % delay rate requiring intervention
    'optimization_min_improvement': 10,  # Minimum % improvement for recommendations
}

# Driver Configuration
DRIVER_LOOKUP_PATH = '/Workspace/Users/pinky.somwani.cs17@ggits.net/delivery-driver-streaming-pipeline/config/driver_lookup.csv'

# Data Quality Filters
DATA_QUALITY_RULES = {
    'max_speed_kmh': 150,  # Maximum realistic speed
    'min_speed_kmh': 0,  # Minimum speed
    'require_coordinates': True,  # Latitude and longitude must not be null
}

# Partitioning Configuration
PARTITION_COLUMNS = {
    'bronze': None,  # No partitioning in bronze
    'silver': 'route_city',  # Partition by city
    'gold': None,  # Gold is typically small enough not to partition
}

# Delta Lake Configuration
DELTA_CONFIG = {
    'overwrite_schema': True,  # Allow schema evolution
    'optimize_write': True,  # Enable optimized writes
    'auto_compact': True,  # Enable auto-compaction
}

# Alerting Configuration (for production)
ALERTING_CONFIG = {
    'enabled': False,  # Set to True in production
    'channels': {
        'email': {
            'enabled': False,
            'recipients': ['ops-team@example.com'],
        },
        'slack': {
            'enabled': False,
            'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        },
        'pagerduty': {
            'enabled': False,
            'integration_key': 'YOUR_INTEGRATION_KEY',
        },
    },
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Helper function to get full path
def get_path(layer: str, dataset: str = None) -> str:
    """
    Get full S3 path for a given layer and dataset.
    
    Args:
        layer: 'bronze', 'silver', or 'gold'
        dataset: Optional dataset name within the layer
    
    Returns:
        Full S3 path
    """
    base_paths = {
        'bronze': BRONZE_PATH,
        'silver': SILVER_PATH,
        'gold': GOLD_PATH,
    }
    
    base = base_paths.get(layer)
    if not base:
        raise ValueError(f"Invalid layer: {layer}. Must be 'bronze', 'silver', or 'gold'")
    
    return f"{base}{dataset}/" if dataset else base

# Export commonly used variables
__all__ = [
    'AWS_REGION',
    'KINESIS_STREAM_NAME',
    'S3_BUCKET',
    'BRONZE_PATH',
    'SILVER_PATH',
    'GOLD_PATH',
    'STREAMING_CONFIG',
    'BUSINESS_RULES',
    'DATA_QUALITY_RULES',
    'get_path',
]