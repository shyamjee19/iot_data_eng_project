from pyspark.sql import SparkSession

# CREATE SPARK SESSION
spark = SparkSession.builder \
    .appName("IoTStreaming") \
    .master("local[*]") \
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"
    ) \
    .getOrCreate()

# READ FROM KAFKA
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "iot-telemetry") \
    .load()

# CONVERT VALUE TO STRING
json_df = kafka_df.selectExpr("CAST(value AS STRING)")

# PRINT STREAM
query = json_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()