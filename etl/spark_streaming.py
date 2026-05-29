import sys
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Add project root directory to path to enable settings import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configs import settings

print("Starting Apache Spark Structured Streaming Job...")

# CREATE SPARK SESSION
spark = SparkSession.builder \
    .appName("IoTStreaming") \
    .master("local[*]") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
    ) \
    .getOrCreate()

# Set logging level to WARN to reduce console spam
spark.sparkContext.setLogLevel("WARN")

# READ FROM KAFKA
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", ",".join(settings.KAFKA_BOOTSTRAP_SERVERS)) \
    .option("subscribe", settings.KAFKA_TOPIC) \
    .load()

# Define structural schema for IoT Telemetry JSON parsing
telemetry_schema = StructType([
    StructField("device_id", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("vibration", DoubleType(), True),
    StructField("pressure", DoubleType(), True),
    StructField("event_time", StringType(), True)
])

# Parse the binary value payload to JSON and schema-bind the fields
parsed_df = kafka_df \
    .selectExpr("CAST(value AS STRING) as json_string") \
    .select(from_json(col("json_string"), telemetry_schema).alias("data")) \
    .select("data.*")

# PRINT STREAM TO CONSOLE IN TABULAR STRUCTURE
print(f"Subscribed to Kafka topic '{settings.KAFKA_TOPIC}'. Streaming formatted data output...")
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()